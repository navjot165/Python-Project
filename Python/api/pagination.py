from rest_framework import status
from rest_framework.response import Response 
from rest_framework.pagination import PageNumberPagination
from accounts.constants import *
from django.core.paginator import Paginator


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10
    def get_paginated_response(self, data):
        return Response({
            "data": data,
            "meta": {
                'page_count':self.page.paginator.num_pages,
                'total_results': self.page.paginator.count,
                'current_page_no': self.page.number,
                'limit': self.page_size,
                'last_page': self.page.has_next()
            }},
            status=status.HTTP_200_OK
        )
        

def GetPagesData(page, data):
	if page:
		if str(page) == '1':
			start = 0
			end = start + API_PAGINATION
		else:
			start = API_PAGINATION * (int(page)-1)
			end = start + API_PAGINATION
	else:
		start = 0
		end = start + API_PAGINATION
	page_data_value = Paginator(data, API_PAGINATION)	
	last_page = True if page_data_value.num_pages == int(page if page else 1) else False
	meta_data = { 
		"page_count": page_data_value.num_pages,
		"total_results": data.count(),
		"current_page_no": int(page if page else 1),
		"limit": API_PAGINATION,
		"last_page": last_page
	}
	return start,end,meta_data