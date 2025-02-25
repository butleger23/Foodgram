from rest_framework.pagination import PageNumberPagination

class UserPaginationClass(PageNumberPagination):
    page_size_query_param = 'limit'