---
paths:
  - "**/views/**/*.py"
  - "**/views.py"
---

# 视图设计规范

## 核心要求

- 返回体使用 JsonResponse 构造

## 详情视图

- 必须通过 `dispatch` 预取实例并赋值给 `self.instance`
- `dispatch` 中捕获 `DoesNotExist` 异常，返回 404 + 中文 `msg`
- 后续方法（`get` / `put` / `delete`）直接使用 `self.instance`，禁止重复查询

## 正确示例

```python
from apps.SM.user.models import User

class UserDetailView(views.APIView):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.instance = User.objects.get(id=kwargs.get('id'))
        except User.DoesNotExist:
            return JsonResponse({
                'msg': '数据不存在',
                'data': None
            }, status=404)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response({
            'msg': 'success',
            'data': UserDetailSerializer(self.instance).data
        })
```

## 错误示例

```python
# ❌ 未在 dispatch 中预取，在 get 中重复查询
class UserDetailView(views.APIView):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs.get('id'))  # ❌
        ...

# ❌ except 裸捕获，未指定 DoesNotExist
    def dispatch(self, request, *args, **kwargs):
        try:
            self.instance = User.objects.get(id=kwargs.get('id'))
        except:  # ❌
            ...
```