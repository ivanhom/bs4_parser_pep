import logging
import re
from typing import Optional
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from requests_cache.session import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, EXPECTED_STATUS, LATEST_VERSION_PATTERN,
                       MAIN_DOC_URL, MAIN_PEP_URL, PARSER_TYPE, PDF_A4_PATTERN,
                       HTMLTag)
from outputs import control_output
from utils import find_string, find_tag, get_response


def whats_new(session: CachedSession) -> Optional[list[tuple]]:
    """Выводит список статей и авторов об изменениях в документации Python."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    response = get_response(session, whats_new_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features=PARSER_TYPE)

    main_div = find_tag(
        soup, HTMLTag.SECTION, attrs={'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        main_div, HTMLTag.DIV, attrs={'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        HTMLTag.LI, attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    for section in tqdm(sections_by_python, desc='Сбор данных'):
        version_a_tag = find_tag(section, HTMLTag.A)
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        response = get_response(session, version_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, features=PARSER_TYPE)
        h1 = find_tag(soup, HTMLTag.H1)
        dl = find_tag(soup, HTMLTag.DL)
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session: CachedSession) -> Optional[list[tuple]]:
    """Выводит список последних версий Python."""
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features=PARSER_TYPE)

    sidebar = find_tag(
        soup, HTMLTag.DIV, attrs={'class': 'sphinxsidebarwrapper'}
    )
    ul_tags = sidebar.find_all(HTMLTag.UL)

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all(HTMLTag.A)
            break
        else:
            raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(LATEST_VERSION_PATTERN, a_tag.text)
        if text_match is None:
            version = a_tag.text
            status = ''
        else:
            version, status = text_match.groups()
        results.append((link, version, status))

    return results


def download(session: CachedSession) -> None:
    """Загрузка последней версии документации Python."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features=PARSER_TYPE)

    table_tag = find_tag(soup, HTMLTag.TABLE, attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, HTMLTag.A, {'href': re.compile(PDF_A4_PATTERN)}
    )

    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session: CachedSession) -> Optional[list[tuple]]:
    """Вывод статусов и количества PEP документов для каждого статуса."""
    response = get_response(session, MAIN_PEP_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features=PARSER_TYPE)

    all_pep_table = find_tag(
        soup, HTMLTag.SECTION, attrs={'id': 'numerical-index'}
    )
    table_body = find_tag(all_pep_table, HTMLTag.TBODY)
    all_pep_tags = table_body.find_all(HTMLTag.TR)

    all_pep = []
    different_statuses = []
    all_statuses = []
    for tag in tqdm(all_pep_tags, desc='Сбор данных'):
        tag_outer_status = find_tag(tag, HTMLTag.TD)
        outer_status = EXPECTED_STATUS[tag_outer_status.text[1:]]
        tag_link = find_tag(tag, HTMLTag.A)
        link = tag_link['href']
        full_link = urljoin(MAIN_PEP_URL, link)

        response = get_response(session, full_link)
        if response is None:
            return
        soup = BeautifulSoup(response.text, features=PARSER_TYPE)
        before_status_tag = find_string(soup, string='Status')
        status_tag = before_status_tag.parent.next_sibling.next_sibling
        inner_status = status_tag.text
        if inner_status not in outer_status:
            different_statuses.append((outer_status, full_link, inner_status))
        all_pep.append((outer_status, full_link, inner_status))
        all_statuses.append(inner_status)

    results = [('Статус', 'Количество')]

    all_uniq_statuses = sorted(list({i[2] for i in all_pep}))
    for i in all_uniq_statuses:
        results.append((i, all_statuses.count(i)))
    results.append(('Total', len(all_pep)))

    if different_statuses:
        for i in different_statuses:
            logging.warning(f'Несовпадающие статусы у {i[1]}. '
                            f'Статус в карточке: {i[2]}. '
                            f'Ожидаемые статусы: {i[0]}.')

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main() -> None:
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()

    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')
    logging.info('============================')


if __name__ == '__main__':
    main()
