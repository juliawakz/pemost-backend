from django.conf import settings
from rest_framework.pagination import PageNumberPagination


def custom_paginate(
    queryset,
    request,
    serializer,
    page_size=settings.REST_FRAMEWORK.get("PAGE_SIZE", 10),
):
    paginator = PageNumberPagination()
    paginator.page_size = page_size
    result_page = paginator.paginate_queryset(queryset, request)
    serializer = serializer(result_page, many=True, context={"request": request})

    return paginator.get_paginated_response(serializer.data)
