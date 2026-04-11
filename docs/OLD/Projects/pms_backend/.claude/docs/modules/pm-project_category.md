# PM 项目分类模块 (pm-project_category)

## 模块定位

项目分类模块是 PMS 项目管理系统中负责项目列表**分类统计**的核心模块。它不直接操作项目数据，而是为前端提供项目列表页面的**分类导航统计**功能。

**核心职责**：根据不同维度（项目状态、用户关系）统计项目数量，支撑前端项目列表页面的分类筛选入口。


## 模块职责边界

### 包含的职责

- 生成项目分类统计数据（状态分类 + 个人关系分类）
- 计算各分类下的项目总数和逾期项目数
- 提供统一的分类统计接口

### 不包含的职责

- **不负责**项目列表的具体查询和过滤（由 `pm-project_list` 模块负责）
- **不负责**项目状态的变更（由项目详情、节点模块负责）
- **不负责**关注者关系的维护（由 `pm-project_follower` 模块负责）


## 核心数据模型

### 依赖的模型

| 模型 | 用途 | 关联方式 |
|------|------|----------|
| `Project_List` | 项目主表 | 直接查询 |
| `ProjectFollower` | 项目关注者 | 通过 `project_followers` 反向关联 |
| `Project_Node_Owners` | 节点负责人 | 通过 `node__list` 关联查询 |

### 分类类型枚举

```python
# 状态分类
ALL = '全部'          # state__in=[1, 2, 3, 5]
PRO = '进行中'        # state=1
CHG = '变更中'        # state=3
CHGS = '变更完成'     # state=2, change_project__status='APPROVED'
COM = '已完成'        # state=2
SUS = '已暂停'        # state=4
INPROG = '申请中'     # state=5
CANCEL = '取消立项'   # state=6

# 个人关系分类
RPB = '我负责的'      # owner_id=user_id, state__in=[1, 3]
FLW = '我关注的'      # project_followers__user__id=user_id, state__in=[1, 3]
IND = '我参与的'      # 通过节点负责人关联
```


## 权限验证流程

### 认证要求

- **接口级别认证**：需要用户登录（`IsAuthenticated`）
- **无额外权限验证**：分类统计接口不进行额外的权限验证

### 权限验证代码

```python
class CategoryListView(views.APIView):
    permission_classes = [IsAuthenticated]  # 仅需登录认证
```

### 与权限系统的关系

- **不调用** `apps.PM.authority` 模块的权限验证
- 任何登录用户都可以获取分类统计数据
- 统计结果会根据当前用户 ID 自动过滤个人关系分类（我负责的、我关注的、我参与的）


## 认证与授权区别说明

### 本模块的认证/授权特点

| 项目 | 说明 |
|------|------|
| **认证 (Authentication)** | ✅ 需要，通过 `IsAuthenticated` 确保用户已登录 |
| **授权 (Authorization)** | ❌ 不需要，任何登录用户都可访问，无额外权限检查 |

### 与其他模块对比

| 模块 | 认证 | 授权 | 说明 |
|------|------|------|------|
| `pm-project_category` | ✅ | ❌ | 仅需登录 |
| `pm-project_list` | ✅ | ✅ | 需要权限验证（根据项目详情权限过滤） |
| `pm-project_follower` | ✅ | ✅ | 需要权限验证（操作关注关系需要项目详情权限） |


## 与其他模块关系

### 模块依赖图

```
pm-project_category (本模块)
├── 依赖: PM.project.models.Project_List
├── 依赖: PM.nodelist.models.Project_Node_Owners
├── 依赖: PM.project.follower.models.ProjectFollower
├── 被依赖: 前端项目列表页面
└── 相关: PM.authority (不直接调用，但与项目列表权限相关)
```

### 关键关联

1. **与 `pm-project_follower` 的关系**
   - 本模块通过 `ProjectFollower` 模型查询用户关注的项目
   - 使用 `project_followers__user__id` 进行反向关联查询
   - **重要**：必须使用 `.distinct()` 避免重复计数

2. **与 `pm-nodelist` 的关系**
   - 通过 `Project_Node_Owners` 查询用户参与的项目
   - 使用 `node__list__state` 关联项目状态

3. **与 `pm-project_list` 的关系**
   - 本模块提供的分类数据用于前端筛选项目列表
   - 两者共享相同的项目状态枚举定义


## 常见业务场景

### 场景 1：前端项目列表页面加载

**流程**：
1. 前端调用 `GET /pm/projects/category`
2. 后端返回所有分类的统计数据
3. 前端根据统计数据渲染分类导航栏
4. 用户点击某个分类后，调用 `GET /pm/projects` 并传递对应的过滤参数

### 场景 2：关注项目后统计更新

**流程**：
1. 用户添加关注：`POST /pm/project/{id}/follower`
2. 前端重新调用 `GET /pm/projects/category`
3. "我关注的"分类的 `total` 数量增加

### 场景 3：项目状态变更后统计更新

**流程**：
1. 项目状态从"进行中"变为"已完成"
2. 前端重新调用分类接口
3. "进行中"分类的 `total` 减少，"已完成"分类的 `total` 增加


## 技术实现建议（Django）

### 关键查询优化

#### 1. 使用 `.distinct()` 避免重复计数

```python
# ❌ 错误：可能产生重复计数
Project_List.objects.filter(
    project_followers__user__id=user_id
).count()

# ✅ 正确：去重计数
Project_List.objects.filter(
    project_followers__user__id=user_id
).distinct().count()
```

#### 2. 逾期时间判断

```python
from django.utils import timezone

# 使用 timezone.now() 而非 datetime.now()
Project_List.objects.filter(
    deadline_time__lt=timezone.now()
)
```

#### 3. 状态过滤

```python
# 进行中或变更中的项目
Project_List.objects.filter(state__in=[1, 3])

# 变更完成的项目（已完成 + 有已批准的变更记录）
Project_List.objects.filter(
    state='2',
    change_project__status='APPROVED'
)
```

### 代码结构建议

```python
# serializers.py
class CategoryListSerializer(serializers.Serializer):
    def generate_category(self):
        # 定义内部函数处理特定统计逻辑
        def count_func_1():  # 我关注的
            ...
        def count_func_2():  # 我参与的
            ...

        # 返回分类列表
        return [...]
```


## API 规范文档

### 接口定义

#### 获取项目分类统计

**请求**
```
GET /pm/projects/category
```

**请求头**
```
Authorization: Bearer <token>
```

**响应示例**
```json
{
  "msg": "success",
  "data": [
    {
      "type": "ALL",
      "name": "全部",
      "total": 150,
      "overdue": 12
    },
    {
      "type": "PRO",
      "name": "进行中",
      "total": 85,
      "overdue": 8
    },
    {
      "type": "CHG",
      "name": "变更中",
      "total": 15,
      "overdue": 2
    },
    {
      "type": "CHGS",
      "name": "变更完成",
      "total": 8,
      "overdue": 0
    },
    {
      "type": "COM",
      "name": "已完成",
      "total": 30,
      "overdue": 0
    },
    {
      "type": "SUS",
      "name": "已暂停",
      "total": 5,
      "overdue": 1
    },
    {
      "type": "INPROG",
      "name": "申请中",
      "total": 7,
      "overdue": 1
    },
    {
      "type": "CANCEL",
      "name": "取消立项",
      "total": 0,
      "overdue": 0
    },
    {
      "type": "RPB",
      "name": "我负责的",
      "total": 12,
      "overdue": 2
    },
    {
      "type": "FLW",
      "name": "我关注的",
      "total": 25,
      "overdue": 3
    },
    {
      "type": "IND",
      "name": "我参与的",
      "total": 45,
      "overdue": 5
    }
  ]
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | string | 分类代码，用于前端筛选 |
| `name` | string | 分类显示名称 |
| `total` | number | 该分类下的项目总数 |
| `overdue` | number | 该分类下的逾期项目数 |


## 扩展设计策略

### 添加新的分类类型

如果需要添加新的项目分类（如"我创建的"、"我评价的"等），按以下步骤操作：

1. **在 `enums.py` 中添加新的分类类型**
```python
project_type = [
    ...
    ('CREATED', '我创建的'),  # 新增
]
```

2. **在 `CategoryListSerializer.generate_category()` 中添加统计逻辑**
```python
def count_func_created():
    """计算我创建的项目统计"""
    return {
        'total': Project_List.objects.filter(
            creator__id=userinfo['id'], state__in=[1, 3]
        ).count(),
        'overdue': Project_List.objects.filter(
            creator__id=userinfo['id'], state__in=[1, 3],
            deadline_time__lt=timezone.now()
        ).count()
    }

# 在返回列表中添加
{
    'type': 'CREATED',
    'name': '我创建的',
    **count_func_created()
}
```

### 添加新的统计维度

如果需要添加其他统计维度（如按部门、按客户等），建议：

1. 创建新的序列化器方法（不修改现有的 `generate_category()`）
2. 在视图中添加新的接口端点

```python
# serializers.py
class DepartmentCategorySerializer(serializers.Serializer):
    def generate_department_category(self):
        """按部门统计项目"""
        ...

# views.py
class DepartmentCategoryListView(views.APIView):
    def get(self, request, *args, **kwargs):
        ...
```


## 演进方向 (Future Evolution)

### 当前局限性

1. **性能问题**：每次请求都需要执行多次数据库查询
2. **缓存缺失**：没有实现统计数据的缓存机制
3. **实时性**：统计数据实时计算，可能在高并发场景下产生延迟

### 未来优化方向

#### 1. 引入缓存机制

```python
from django.core.cache import cache

class CategoryListView(views.APIView):
    def get(self, request, *args, **kwargs):
        cache_key = f"category_stats_{user_id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return JsonResponse({'msg': 'success', 'data': cached_data})

        # 计算统计数据
        category_data = serializer.generate_category()
        cache.set(cache_key, category_data, timeout=300)  # 缓存5分钟

        return JsonResponse({'msg': 'success', 'data': category_data})
```

#### 2. 异步统计更新

- 使用 Celery 定时任务预计算统计数据
- 存储到 Redis 或专门的统计表中
- 接口直接返回预计算结果

#### 3. 数据库优化

- 为常用查询字段添加复合索引
```python
class Project_List(models.Model):
    ...
    class Meta:
        indexes = [
            models.Index(fields=['state', 'deadline_time']),
            models.Index(fields=['owner_id', 'state']),
        ]
```

#### 4. 按需统计

- 前端可以指定需要哪些分类的统计数据
- 减少不必要的数据库查询


## 模块特有名词索引

| 名词 | 定位 | 说明 |
|------|------|------|
| `CategoryListView` | 视图 | 项目分类列表视图 |
| `CategoryListSerializer` | 序列化器 | 项目分类统计序列化器 |
| `generate_category()` | 方法 | 生成分类统计数据的核心方法 |
| `count_func_1()` | 内部函数 | 计算"我关注的"项目统计 |
| `count_func_2()` | 内部函数 | 计算"我参与的"项目统计 |
| `project_followers` | 关联字段 | ProjectFollower 模型的反向关联名 |
| `FLW` | 分类代码 | 我关注的 |
| `RPB` | 分类代码 | 我负责的 |
| `IND` | 分类代码 | 我参与的 |
