import logging

from requests import RequestException
from exceptions import ParserFindStringException, ParserFindTagException


def get_response(session, url):
    """Обработка запроса к интернет ресурсу."""
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    """Поиск нужного тега в коде страницы."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def find_string(soup, string):
    """Поиск нужной строки в коде страницы."""
    searched_string = soup.find(string=string)
    if searched_string is None:
        error_msg = f'Не найдена строка {string}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindStringException(error_msg)
    return searched_string
