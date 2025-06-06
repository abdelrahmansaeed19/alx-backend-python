from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MessagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'  # optional: allow clients to override
    max_page_size = 100  # optional: prevent huge pages

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
            'page_size': self.get_page_size(self.request),
            'results': data
        })
