from rest_framework import pagination


class YoutubePagination(pagination.PageNumberPagination):
    page_size = 10