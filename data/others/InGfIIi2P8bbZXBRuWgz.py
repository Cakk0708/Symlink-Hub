import os, sys, django, glob, importlib, time, json
from django.conf import settings
from django.db import models
from datetime import datetime

# 路径配置
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

# 初始化Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home.settings')
django.setup()

from django.contrib.contenttypes.models import ContentType

class Request:
    user: None
    method: None

    def __init__(self, user_instance):
        self.user = user_instance

class Debug:
    request = None

    def __init__(self, request):
        self.request = request
    
    def view_post(self, Serializer):
        serializer_res = Serializer(
            data=self.request.data, context={'request': self.request}
        )

        if not serializer_res.is_valid():
            print(
                {'msg': '数据验证失败', 'errors': serializer_res.errors}
            )
            exit()
            
        last_data = serializer_res.save()

        print({
            'msg': "数据添加成功！",
            "data": {'insertedId': last_data.id}
        })

    def view_put(self, instance, Serializer):
        serializer_res = Serializer(
            instance, data=self.request.data, context={'request': self.request}
        )

        if not serializer_res.is_valid():
            print(
                {'msg': '数据验证失败', 'errors': serializer_res.errors}
            )
            exit()
            
        serializer_res.save()

        print({
            'msg': "success"
        })

    def view_get_list(self, queryset, Serializer):
        from utils.serializer.params_handle import ParamsSerializer
        from utils.task_profiler import PrintSql

        serializer = ParamsSerializer(
            data={
                'pageSize': 100
            },
            context={
                'request': self.request,
                'list_serializer': Serializer
            }
        )
        if not serializer.is_valid():
            print({'msg': '数据验证失败', 'errors': serializer.errors})
            exit()

        paginated_queryset, pagination = serializer.get_paginated(
            queryset
        )

        data = Serializer(
            paginated_queryset, 
            many=True, 
            context={
                'request': self.request, 
            }
        ).data

        path_name = '%s_%s.txt'%(
            ContentType.objects.get_for_model(queryset.model).model,
            str(int(time.time()))
        )
        PrintSql().save(path_name)

        print({'items': data, 'pagination': pagination})

        self.save(
            ContentType.objects.get_for_model(queryset.model).model,
            {'items': data, 'pagination': pagination}
        )

    def view_get_detail(self, instance, Serializer):
        serializer = Serializer(
            instance, context={'request': self.request}
        )
        
        self.save(
            ContentType.objects.get_for_model(instance).model,
            serializer.data
        )

    def save(self, model, data):
        from django.http import JsonResponse
        
        data = JsonResponse(data, json_dumps_params={'ensure_ascii': False})

        date = '%s-%s-%s'%(
            datetime.now().year,
            str(datetime.now().month).zfill(2),
            str(datetime.now().day).zfill(2)
        )
        path_name = '%s_%s.json'%(
            model,
            str(int(time.time()))
        )

        if not os.path.exists(f'cache/{date}'):
            os.makedirs(f'cache/{date}')

        with open(f'cache/{date}/data_{path_name}', 'w', encoding='utf-8') as f:
            f.write(data.content.decode('utf-8'))
        
        print(f"Json Data Path: {os.path.abspath(f'cache/{date}/data_{path_name}')}")

if __name__ == '__main__':
    from apps.SM.user.models import User

    argv = sys.argv
    # try:
    module = importlib.import_module(f"debug.{argv[1]}")
    # except:
    #     print('执行取消')
    #     exit()

    request = Request(User.objects.get(id=1))
    debug = Debug(request)

    module.run(argv[2], debug)
    
    