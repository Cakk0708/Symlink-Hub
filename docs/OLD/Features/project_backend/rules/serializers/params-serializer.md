---
paths:
  - "**/serializers/**/*.py"
  - "**/serializers.py"
---

# 参数处理序列化器（ParamsSerializer）规范

## 字段

- 必须包含 `keywords` 字段
- 必须包含 `page` 字段
- 必须包含 `orderNo` 字段

## 正确示例

```python
class ListParamsSerializer(serializers.Serializer):
    """订单查询参数序列化器"""

    keywords = serializers.CharField(
        required=False
    )
    orderNo = serializers.CharField(
        source='order_no',
        required=False
    )
    page = serializers.IntegerField(required=False)

    def get_queryset(self, queryset):
        """根据查询参数过滤查询集"""

        query = models.Q()

        # 组织过滤：只查询当前用户组织的订单
        query &= models.Q(organization=self.context.get('request').user.organization)

        if orderNo := self.validated_data.get('orderNo'):
            query &= models.Q(id=orderNo)

        if keywords := self.validated_data.get('keywords'):
            query &= models.Q(
                models.Q(account__username__icontains=keywords) |
                models.Q(account__nickname__icontains=keywords) |
                models.Q(account__email__icontains=keywords) |
                models.Q(account__phone__icontains=keywords) |
                models.Q(account__remark__icontains=keywords) |
                models.Q(account__customer__name__icontains=keywords)
            )

        queryset = queryset.filter(query)
        
        page = self.validated_data.get('page', 0)
        page_size = 10
        start, end = page * page_size, (page + 1) * page_size
        
        pagination = {
            'page': page,
            'pageSize': page_size,
            'total': queryset.count()
        }

        queryset = queryset[start:end]

        return queryset, pagination

```
