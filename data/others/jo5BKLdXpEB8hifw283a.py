from utils.serializer.params_handle import ParamsSerializer

from apps.MES.prcmat.v3.utils import (
    get_list_queryset,
)
from apps.MES.prcmat.v3.serializers import (
    ListSerializer,
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

def get_process_list(request):
    request.method = 'GET'
    queryset = get_process_queryset()

    serializer = ParamsSerializer(
        data={
            'pageSize': 100
        },
        context={
            'request': request,
            'list_serializer': ProcessListSerializer
        }
    )
    if not serializer.is_valid():
        print({'msg': '数据验证失败', 'errors': serializer.errors})
        exit()

    paginated_queryset, pagination = serializer.get_paginated(
        queryset
    )

    items = ProcessListSerializer(
        paginated_queryset, many=True,
        context={'request': request}
    ).data

    return {
        'items': items,
        'pagination': pagination
    }

def get_detail(request):
    request.method = 'GET'
    instance = get_queryset().get(id=20)

    return ReprecSerializer(
        instance, context={'request': request}
    ).data

def for_queryset(request):
    fields = [
        'id',
    ]
    for instance in get_list_queryset():
        for field in fields:
            print(f'{field}: ', getattr(instance, field))
        
        print('')



