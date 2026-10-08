from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Default page-number pagination for the project's REST APIs.

    Clients (web / mobile / desktop) can request a page with ``?page=N`` and
    override the page size with ``?page_size=M`` (capped at ``max_page_size``).
    """

    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 200
