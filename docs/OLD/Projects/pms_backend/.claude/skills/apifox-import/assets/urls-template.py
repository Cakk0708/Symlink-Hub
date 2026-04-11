# Django REST Framework URL 配置模板

from rest_framework.routers import DefaultRouter
from .views import {{ModelName}}ViewSet

app_name = '{{app_name}}'  # 如: 'bdm'

router = DefaultRouter()
router.register(
    r'{{resource_plural}}',  # 资源复数形式，如: customers
    {{ModelName}}ViewSet,
    basename='{{resource_singular}}'  # 资源单数形式，如: customer
)

urlpatterns = router.urls

# 生成的路由：
# GET    /bdm/{{resource_plural}}/              → list()
# POST   /bdm/{{resource_plural}}/              → create()
# GET    /bdm/{{resource_plural}}/{id}/         → retrieve()
# PUT    /bdm/{{resource_plural}}/{id}/         → update()
# PATCH  /bdm/{{resource_plural}}/{id}/         → partial_update()
# DELETE /bdm/{{resource_plural}}/              → destroy() (批量)
# PATCH  /bdm/{{resource_plural}}/batch_update/ → batch_update() (自定义)
