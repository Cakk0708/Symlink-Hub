---
paths:
  - "**/views/**/*.py"
  - "**/views.py"
---

# 视图设计规范

## 核心要求

- 所有视图必须继承 `views.APIView`，禁止使用 `generics.*` 或 `viewsets.*`
- 返回体使用 JsonResponse 构造

## 列表视图

- 返回结构必须包含 `msg` 和 `data`
- 列表数据禁止在 `data` 下直接返回数组，必须用 `items` + `count` 包裹
- Query 参数必须遵循 `snake_case` 规范

## 正确示例

```python
class UserListView(views.APIView):
    def get(self, request, *args, **kwargs):
        queryset = User.objects.all()
        return JsonResponse({
            'msg': 'success',
            'data': {
                'items': UserListSerializer(queryset, many=True).data,
                'count': queryset.count()
            }
        })
```

## 错误示例

```python
# ❌ data 下直接返回数组，缺少 items/count 包裹
return Response({
    'msg': 'success',
    'data': UserListSerializer(queryset, many=True).data
})

# ❌ 缺少 count 字段
# ❌ 使用 Response
return Response({
    'msg': 'success',
    'data': {
        'items': UserListSerializer(queryset, many=True).data
    }
})
```
