# Django REST Framework 视图集代码模板

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import {{ModelName}}
from .serializers import {{ModelName}}Serializer, {{ModelName}}ListSerializer


class {{ModelName}}ViewSet(viewsets.ModelViewSet):
    """
    {{模型名称}}视图集

    列表接口: GET /bdm/{{resource_plural}}/
    详情接口: GET /bdm/{{resource_plural}}/{id}/
    创建接口: POST /bdm/{{resource_plural}}/
    更新接口: PUT /bdm/{{resource_plural}}/{id}/
    删除接口: DELETE /bdm/{{resource_plural}}/
    """

    queryset = {{ModelName}}.objects.all()
    serializer_class = {{ModelName}}Serializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return {{ModelName}}ListSerializer
        return {{ModelName}}Serializer

    def create(self, request):
        """
        创建{{模型名称}}

        请求体格式: { "models": [...] }
        响应格式: { "models": [...] }
        """
        models_data = request.data.get('models', [])

        if not models_data:
            return Response(
                {"error": "models字段不能为空"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=models_data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({"models": serializer.data}, status=status.HTTP_201_CREATED)

    def destroy(self, request):
        """
        批量删除{{模型名称}}

        请求体格式: { "ids": [...] }
        """
        ids = request.data.get('ids', [])

        if not ids:
            return Response(
                {"error": "ids字段不能为空"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 批量删除
        deleted_count, _ = {{ModelName}}.objects.filter(id__in=ids).delete()

        return Response(
            {"deleted_count": deleted_count},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['patch'])
    def batch_update(self, request):
        """
        批量部分更新（如批量禁用）

        请求体格式: { "ids": [...], "disable_flag": true }
        """
        ids = request.data.get('ids', [])
        disable_flag = request.data.get('disable_flag')

        if not ids:
            return Response(
                {"error": "ids字段不能为空"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 批量更新
        updated_count = {{ModelName}}.objects.filter(
            id__in=ids
        ).update(disable_flag=disable_flag)

        return Response(
            {"updated_count": updated_count},
            status=status.HTTP_200_OK
        )
