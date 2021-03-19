from typing import Union, Dict
from math import ceil
from contextlib import contextmanager


@contextmanager
def ignore_exception(*exceptions) -> None:
    """
    Ignores the given exceptions

    Parameters
    ----------
    *exceptions: The exceptions you want to ignore

    Returns
    ----------
    None
    """

    try:
        yield
    except (exceptions):
        pass


def paginator(content: list, page: int) -> Dict[str, Union[int, str]]:
    """
    Divides content into 10 element pages

    Parameters
    -----------
    content: A list of strings
    page: The page

    Returns
    -----------
    (dict): A dictionay containing content and metadata
        keys: pagecount, page, page_content
    """

    pagecount = ceil(len(content) / 10)

    if not page or page <= 0 or page > pagecount:
        page = 1

    start_index = (page - 1) * 10
    end_index = page * 10

    page_content = content[start_index:end_index]

    page_data = {
        'pagecount': pagecount,
        'page': page,
        'page_content': page_content
    }
    return page_data
