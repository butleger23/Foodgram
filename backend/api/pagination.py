from rest_framework.pagination import PageNumberPagination


DEFAULT_PAGE_SIZE = 10

class CustomPaginationClass(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'limit'
