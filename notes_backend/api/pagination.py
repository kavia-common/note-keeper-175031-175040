from rest_framework.pagination import PageNumberPagination

# PUBLIC_INTERFACE
class StandardResultsSetPagination(PageNumberPagination):
    """Pagination class supporting ?page_size=... with a sensible cap.

    - Default page size: 10
    - Query parameters:
        - page: page number
        - page_size: number of items per page (capped by max_page_size)
    - Max page size: 100
    """
    page_size = 10
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = 100
