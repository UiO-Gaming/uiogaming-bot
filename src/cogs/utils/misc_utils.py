from contextlib import contextmanager
from math import ceil


@contextmanager
def ignore_exception(*exceptions: Exception):
    """
    Ignores the given exceptions

    Parameters
    ----------
    *exceptions tuple[Exception]: The exceptions you want to ignore
    """

    try:
        yield
    except exceptions:
        pass


class Paginator:
    def __init__(self, content: list):
        self.content = content
        self.total_page_count = ceil(len(content) / 10)
        self.current_page = 1

    def get_page(self, page: int) -> list | None:
        """
        Returns the page of the paginator

        Parameters
        ----------
        page (int): The page you want to get

        Returns
        ----------
        (list|None): The page you requested
        """
        if page < 1 or page > self.total_page_count:
            return None

        start_index = (page - 1) * 10
        end_index = page * 10

        return self.content[start_index:end_index]

    def get_current_page(self) -> list:
        """
        Returns the current page of the paginator

        Returns
        ----------
        (list): The current page of the paginator
        """
        return self.get_page(self.current_page)

    def next_page(self) -> list | None:
        """
        Returns the next page of the paginator

        Returns
        ----------
        (list): The next page of the paginator
        """
        self.current_page += 1
        return self.get_page(self.current_page)

    def previous_page(self) -> list | None:
        """
        Returns the previous page of the paginator

        Returns
        ----------
        (list): The previous page of the paginator
        """
        self.current_page -= 1
        return self.get_page(self.current_page)

    def first_page(self) -> list | None:
        """
        Returns the first page of the paginator

        Returns
        ----------
        (list): The first page of the paginator
        """
        self.current_page = 1
        return self.get_page(self.current_page)

    def last_page(self) -> list | None:
        """
        Returns the last page of the paginator

        Returns
        ----------
        (list): The last page of the paginator
        """
        self.current_page = self.total_page_count
        return self.get_page(self.current_page)
