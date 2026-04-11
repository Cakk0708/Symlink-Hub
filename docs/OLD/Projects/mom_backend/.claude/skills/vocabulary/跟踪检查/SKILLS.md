---
name: vocab-trace-check
description: 当用户提到"跟踪检查"、"上查"、"下查"、"单据追溯"、"EntryTrace"、"来源单据"、"下游单据"、"下推"、"单据关联"或要求实现单据关系追溯功能时，必须调用此技能以获取正确的数据模型和代码实现规范。
---

# 跟踪检查业务 (Trace Check)

## 触发关键词
- 跟踪检查、Trace Check、单据追溯、单据关联
- 上查（UP）、下查（DOWN）、来源单据、上游单据
- 下游单据、下推、PUSH关系
- EntryTrace、GenericForeignKey、ContentType关联
- 锚点（anchor）、批量创建关联

## 业务概述

跟踪检查（Trace Check）是 MOM 系统中用于追溯单据关系的功能，主要用于：
- **上查（UP）**：查询当前单据的来源单据（上游单据）
- **下查（DOWN）**：查询当前单据下推生成的下游单据

该功能适用于包含下推业务的模块，如采购入库单可上查采购订单、下查采购退料单。

## 支持的模块

跟踪检查功能已实现于以下模块：

| 模块 | 单据类型 | BillType | 上查 | 下查 |
|------|----------|----------|------|------|
| **PMS（采购管理）** |
| | 采购订单 | ORPURC | - | PURC, REPURC, PLORDER |
| **SMS（销售管理）** |
| | 销售订单 | ORSALE | - | SALSH |
| **WMS（仓库管理）- 入库** |
| | 采购入库单 | PURC | ORPURC | REPURC |
| | 生产入库单 | PRC | WORKORDER | PRCTK, RETPRC |
| | 生产退料单 | RETPRC | PRCTK | - |
| | 售后入库单 | RETIN | - | RETOUT |
| | 盘盈单 | SGI | STOCKTAKE | - |
| **WMS（仓库管理）- 出库** |
| | 销售出库单 | SALSH | ORSALE | - |
| | 生产领料单 | PRCTK | PRC, PRCMAT | RETPRC |
| | 售后出库单 | RETOUT | RETIN | - |
| | 采购退料单 | REPURC | PURC, ORPURC | - |
| | 盘亏单 | SLO | STOCKTAKE | - |
| **MES（生产执行）** |
| | 生产工单 | WORKORDER | PLORDER | REPREC, PRC, PRCMAT, PRCTK, RETPRC |
| | 生产报工 | REPREC | WORKORDER | - |
| | 生产用料单 | PRCMAT | WORKORDER | PRCTK |
| **APS（计划与排程）** |
| | 计划订单 | PLORDER | - | ORPURC, WORKORDER |

### 单据关系图

```
                    ORPURC (采购订单)
                          │
                          ▼
                    PURC (采购入库单) ────▶ REPURC (采购退料单)
                          │
                    PLORDER (计划订单)
                          │
                          ▼
                    WORKORDER (生产工单)
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
       REPREC          PRC (生产入库)   PRCMAT (生产用料)
                         │                   │
                    PRCTK (生产领料) ◀──────┘
                         │
                    RETPRC (生产退料)

                    ORSALE (销售订单)
                          │
                          ▼
                    SALSH (销售出库)

                    RETIN (售后入库)
                          │
                          ▼
                    RETOUT (售后出库)
```

## 核心数据模型

### EntryTrace 模型

位置：`apps/SM/entry_trace/models.py`

单据关联关系表，使用 Django 的 GenericForeignKey 实现通用关联：

```python
class EntryTrace(models.Model):
    # 来源单据（上游）
    source_content_type = models.ForeignKey(ContentType, ...)
    source_object_id = models.PositiveIntegerField()
    source_document = GenericForeignKey('source_content_type', 'source_object_id')

    # 目标单据（下游）
    target_content_type = models.ForeignKey(ContentType, ...)
    target_object_id = models.PositiveIntegerField(null=True)
    target_document = GenericForeignKey('target_content_type', 'target_object_id')

    # 关联类型（如：PUSH - 下推）
    relation_type = models.CharField(max_length=50, choices=Choices.RelationType.choices)

    # 锚点（用于批量创建时的临时关联）
    anchor = models.CharField(max_length=64, db_index=True, null=True, blank=True)
```

## 实现流程

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          跟踪检查业务流程                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  1. 前端请求                                                                     │
│     ├─ URL: /api/wms/in-stock/purc/{pk}/trace-check/{mode}/                     │
│     ├─ pk: 单据ID                                                                │
│     └─ mode: 跟踪模式（ORPURC 上查 / REPURC 下查）                               │
│                                                                                 │
│  2. TraceCheckViews (views.py)                                                  │
│     ├─ 获取单据实例                                                              │
│     └─ 调用 TraceCheckSerializer 处理                                            │
│                                                                                 │
│  3. TraceCheckSerializer (serializers.py)                                       │
│     ├─ 接收 mode 参数指定检查方向                                                │
│     ├─ 根据 mode 调用对应的 get_xxx 方法                                         │
│     │   ├─ get_ORPURC(): 上查采购订单                                            │
│     │   └─ get_REPURC(): 下查采购退料单                                          │
│     └─ 通过 EntryTrace 查询关联单据                                              │
│                                                                                 │
│  4. 返回数据                                                                     │
│     └─ { items: [...], pagination: {...} }                                      │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 代码实现参考

### 1. 枚举定义 (enums.py)

位置：`apps/WMS/in_stock/purc/enums.py`

```python
class EntryTrace:
    class TraceCheckModes(models.TextChoices):
        UP = 'UP', '上查'
        DOWN = 'DOWN', '下查'

    # 上查可检查的单据类型
    extra_trace_check_bill_types = {
        'UP': [system_choices.BillType.ORPURC],      # 采购订单
        'DOWN': [system_choices.BillType.REPURC]     # 采购退料单
    }

    # 可用于跟踪检查的所有单据类型
    trace_check_bill_types = [
        system_choices.BillType.ORPURC,
        system_choices.BillType.REPURC
    ]
```

### 2. 视图层 (views.py)

位置：`apps/WMS/in_stock/purc/views.py:277-301`

```python
class TraceCheckViews(APIView):
    def dispatch(self, request, *args, **kwargs):
        self.pk = kwargs.get('pk', None)      # 单据ID
        self.mode = kwargs.get('mode', None)  # 跟踪模式
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            instance = InstockPurc.objects.get(id=self.pk)
        except InstockPurc.DoesNotExist:
            return JsonResponse({'msg': '查询参数"%s"不存在'%self.pk}, status=404)

        # 支持分页和筛选参数
        serializer = TraceCheckSerializer(
            instance,
            data={'mode': self.mode, **request.GET.dict()},
            context={'request': request}
        )

        if serializer.is_valid():
            return JsonResponse({'msg': 'success', 'data': serializer.data})
        else:
            return JsonResponse({
                'msg': '数据验证失败', 'errors': serializer.errors
            }, status=400)
```

**支持的查询参数**：
- `query` - 筛选条件（格式：`字段:方式:值`，如 `code:in:ABC`）
- `pageNum` - 页码（默认：1）
- `pageSize` - 每页数量（默认：15）

### 3. 序列化器 (serializers.py)

位置：`apps/WMS/in_stock/purc/serializers.py:1110-1224`

```python
class TraceCheckSerializer(serializers.ModelSerializer):
    mode = serializers.ChoiceField(
        choices=enumEntryTrace.trace_check_bill_types,
        required=False,
        write_only=True
    )

    # 分页和筛选参数
    query = serializers.CharField(required=False, default=None, write_only=True)
    pageNum = serializers.IntegerField(required=False, default=1, write_only=True)
    pageSize = serializers.IntegerField(required=False, default=15, write_only=True)

    # 定义每种单据类型的查询方法
    ORPURC = serializers.SerializerMethodField()  # 上查采购订单
    REPURC = serializers.SerializerMethodField()  # 下查采购退料单

    class Meta:
        model = InstockPurc
        fields = ['mode', 'query', 'pageNum', 'pageSize', 'ORPURC', 'REPURC']

    def _get_paginated_data(self, queryset, list_serializer_class, module_check=None):
        """内部方法：统一处理分页逻辑"""
        from utils.serializer.params_handle import ParamsSerializer

        # 构建分页参数
        params_data = {}
        if query := self.validated_data.get('query'):
            params_data['query'] = query
        if pageNum := self.validated_data.get('pageNum'):
            params_data['pageNum'] = pageNum
        if pageSize := self.validated_data.get('pageSize'):
            params_data['pageSize'] = pageSize

        serializer = ParamsSerializer(
            data=params_data,
            context={'list_serializer': list_serializer_class}
        )
        serializer.is_valid()
        results, pagination = serializer.get_paginated(queryset)

        # 检查模块订阅状态
        if module_check and module_check in cache.get(
                'SYSTEM:OMC:PLAN:subscribed:module', []
            ):
            return {
                'items': list_serializer_class(
                    results,
                    many=True,
                    context={'request': self.current_request}
                ).data,
                'pagination': pagination
            }
        else:
            return {
                'items': [],
                'pagination': {}
            }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 根据 mode 返回对应的数据
        if mode := self.initial_data.get('mode', None):
            data = data[mode]
        return data

    def get_ORPURC(self, instance):
        """上查采购订单"""
        from apps.PMS.order.serializers import ListSerializer
        from apps.PMS.order.models import PurchaseOrderChilds
        from apps.PMS.order.utils import get_list_queryset

        source_content_type = ContentType.objects.get_for_model(PurchaseOrderChilds)

        source_object_ids = EntryTrace.objects.filter(
            source_content_type=source_content_type,
            target_content_type=ContentType.objects.get_for_model(InstockPurcChilds),
            target_object_id__in=instance.instock_doc_purc_child.values_list('id', flat=True)
        ).values_list('source_object_id', flat=True)

        queryset = get_list_queryset().filter(id__in=source_object_ids)

        return self._get_paginated_data(
            queryset,
            ListSerializer,
            module_check=source_content_type.app_label  # 'PMS'
        )

    def get_REPURC(self, instance):
        """下查采购退料单"""
        from apps.WMS.out_stock.repurc.serializers import ListSerializer
        from apps.WMS.out_stock.repurc.models import OutstockRepurcChilds
        from apps.WMS.out_stock.repurc.utils import get_list_queryset

        target_content_type = ContentType.objects.get_for_model(OutstockRepurcChilds)

        target_object_ids = EntryTrace.objects.filter(
            source_content_type=ContentType.objects.get_for_model(InstockPurcChilds),
            source_object_id__in=instance.instock_doc_purc_child.values_list('id', flat=True),
            target_content_type=target_content_type
        ).values_list('target_object_id', flat=True)

        queryset = get_list_queryset().filter(id__in=target_object_ids)

        return self._get_paginated_data(
            queryset,
            ListSerializer,
            module_check=target_content_type.app_label  # 'WMS'
        )
```

**关键点**：
1. `query`、`pageNum`、`pageSize` 字段标记为 `write_only=True`，仅用于输入
2. `_get_paginated_data` 内部方法封装分页逻辑，避免代码重复
3. `module_check` 使用 `ContentType.app_label` 动态检查模块订阅状态
4. `source_content_type` 复用，避免重复调用 `get_for_model`

## 关联关系创建

在单据下推时创建 EntryTrace 记录，示例（采购入库单创建时）：

```python
# serializers.py:875-902
for index, child in enumerate(childs_data):
    anchor = f"{Choices.BillType.PURC}:{doc_instance.code}:{index}"

    if child and 'source_orpurc_child' in child:
        source_content_type = ContentType.objects.get_for_model(PurchaseOrderChilds)
        target_content_type = ContentType.objects.get_for_model(InstockPurcChilds)
        source_object_instance = child.pop('source_orpurc_child')

        bulk_traces_create_data.append(
            EntryTrace(
                source_content_type=source_content_type,
                source_object_id=source_object_instance.id,
                target_content_type=target_content_type,
                relation_type=entryTraceChoices.RelationType.PUSH,
                anchor=anchor,  # 临时锚点，批量创建后更新
                creator=self.current_user
            )
        )

EntryTrace.objects.bulk_create(bulk_traces_create_data)
```

## API 端点示例

```
# 基本请求
GET /api/wms/in-stock/purc/{pk}/trace-check/ORPURC/
# 上查采购订单

GET /api/wms/in-stock/purc/{pk}/trace-check/REPURC/
# 下查采购退料单

# 带分页和筛选
GET /api/wms/in-stock/purc/{pk}/trace-check/ORPURC/?pageNum=1&pageSize=20
GET /api/wms/in-stock/purc/{pk}/trace-check/REPURC/?query=code:in:PO&pageNum=1&pageSize=15
```

## 响应格式

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 123,
        "code": "PO202501001",
        ...
      }
    ],
    "pagination": {
      "total": 10,
      "page": 1,
      "pageSize": 20
    }
  }
}
```
