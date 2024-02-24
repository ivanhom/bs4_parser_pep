import logging
from typing import Optional, Union

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from requests import RequestException
from requests_cache.models.response import CachedResponse
from requests_cache.session import CachedSession

from constants import ENCODING_STANDART
from exceptions import ParserFindStringException, ParserFindTagException


def get_response(
        session: CachedSession,
        url: str
) -> Optional[CachedResponse]:
    """Обработка запроса к интернет ресурсу."""
    try:
        response = session.get(url)
        response.encoding = ENCODING_STANDART
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(
        soup: Union[BeautifulSoup, Tag],
        tag: str,
        attrs: Optional[dict] = None
) -> Optional[Tag]:
    """Поиск нужного тега в коде страницы."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def find_string(
        soup: BeautifulSoup,
        string: str
) -> Optional[NavigableString]:
    """Поиск нужной строки в коде страницы."""
    searched_string = soup.find(string=string)
    if searched_string is None:
        error_msg = f'Не найдена строка {string}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindStringException(error_msg)
    return searched_string
