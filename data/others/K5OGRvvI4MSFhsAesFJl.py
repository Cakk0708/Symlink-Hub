from utils.serializer.params_handle import ParamsSerializer

from apps.APS.plorder.utils import (
    get_list_queryset, get_detail_queryset
)
from apps.APS.plorder.serializers import (
    ListSerializer,
    DetailSerializer,
    # TraceCheckSerializer
)

def get_list(request):
    request.method = 'GET'
    queryset = get_list_queryset()

    serializer = ParamsSerializer(
        data={
            'pageSize': 100
        },
        context={
            'request': request,
            'list_serializer': ListSerializer
        }
    )
    if not serializer.is_valid():
        print({'msg': '数据验证失败', 'errors': serializer.errors})
        exit()

    paginated_queryset, pagination = serializer.get_paginated(
        queryset
    )

    items = ListSerializer(
        paginated_queryset, many=True,
        context={'request': request}
    ).data

    return {
        'items': items,
        'pagination': pagination
    }

def get_detail(request):
    request.method = 'GET'
    instance = get_detail_queryset().get(id=1380)

    return DetailSerializer(
        instance, context={'request': request}
    ).data

def get_queryset(request):
    fields = [
        'id',
        'root_document_type',
    ]
    for instance in get_list_queryset():
        for field in fields:
            print(f'{field}: ', getattr(instance, field))
        
        print('')
