# APS 订单模块 (Order) 技能说明

## 模块定位

APS (Asynchronous Processing System) 订单模块是 Duolingo 自动化任务调度与执行的核心系统。该模块负责管理用户的自动化业务订单（如经验获取、宝石收集、签到等），并通过 Celery 异步任务框架实现定时调度和自动执行。

**技术架构**：
- 后端框架：Django 5.1.7 + Django REST Framework
- 异步任务：Celery (Redis 作为消息代理)
- 模块位置：`apps/APS/orders/`

## 模块职责边界

### 核心职责
1. **订单生命周期管理**：创建、调度、执行、完成、取消
2. **任务分类处理**：支持多种业务类型（exp/gems/3x_xp/sign）
3. **状态机控制**：管理订单在不同状态间的流转
4. **异步调度**：通过 Celery 实现订单的定时执行
5. **进度跟踪**：记录计划数量与完成数量

### 边界清晰性
- **不属于本模块**：用户账号管理（BDM/Account）、Duolingo API 调用逻辑（apps/API）、Redis 缓存策略（utils/redis）
- **本模块职责**：订单数据模型、状态流转逻辑、任务调度封装

## 核心数据模型

### Order 主模型 (`apps/APS/orders/models.py`)

```python
class Order(models.Model):
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    planned_qty = models.IntegerField(default=0)          # 计划数量
    plan_duration = models.IntegerField(default=60)       # 计划持续时间(分钟)
    completed_qty = models.IntegerField(default=0)        # 已完成数量
    before_value = models.IntegerField(default=0)         # 初始值(用于计算增量)

    task_id = models.CharField(max_length=100, null=True, blank=True)  # Celery 任务 ID

    category = models.CharField(choices=Choices.category)   # 业务分类
    status = models.CharField(choices=Choices.status)       # 订单状态
    business = models.CharField(choices=Choices.business)   # 付费/免费

    account = models.ForeignKey('BDM.Account', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, null=True, blank=True)

    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True)
    schedule_at = models.DateTimeField(null=True)

    version = models.IntegerField(default=1)                # 版本号：v1=1, v2=2
```

### v2 子模型

**OrderExp（经验订单）**

```python
class OrderExp(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='exp')
    before_value = models.IntegerField(default=0)         # 初始经验值
    plan_duration = models.IntegerField(default=60)       # 计划持续时间（分钟）
    schedule_at = models.DateTimeField(null=True)         # 计划执行时间
    planned_qty = models.IntegerField(default=0)          # 计划数量
    completed_qty = models.IntegerField(default=0)        # 完成数量
```

**OrderGem（宝石订单）**

```python
class OrderGem(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='gem')
    before_value = models.IntegerField(default=0)         # 初始宝石值
    planned_qty = models.IntegerField(default=0)          # 计划数量
    completed_qty = models.IntegerField(default=0)        # 完成数量
```

**OrderThreeXP（三倍经验订单）**

```python
class OrderThreeXP(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='three_xp')
    planned_qty = models.IntegerField(default=0)          # 计划领取次数
    completed_qty = models.IntegerField(default=0)        # 已领取次数
```

**OrderSigning（签到订单）**

```python
class OrderSigning(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='signing')
    start_date = models.DateField()                       # 开始日期
    end_date = models.DateField()                         # 结束日期
    execution_time = models.CharField(max_length=10)      # 执行时间（HH:MM）
    planned_qty = models.IntegerField(default=0)          # 每日经验目标总量
```

> **注意**：`OrderSigning` 没有 `completed_qty` 字段，每日完成数量通过局部变量 `accumulated_exp` 在执行时累加，最终写入主订单的 `completed_qty`。

### 枚举定义 (`apps/APS/orders/enums.py`)

**状态值 (Choices.OrderStatus)**：
- `waiting` - 等待执行
- `doing` - 执行中
- `done` - 已完成
- `pause` - 暂停
- `cancel` - 已取消
- `error` - 执行错误

**业务分类 (Choices.OrderCategory)**：
- `exp` - 经验值获取任务
- `gems` - 宝石收集任务
- `3x_xp` - 三倍经验激活任务
- `sign` - 每日签到任务

**业务类型 (Choices.OrderBusiness)**：
- `paid` - 付费订单
- `free` - 免费订单

## 版本对比

| 特性 | v1 (version=1) | v2 (version=2) |
|------|---------------|---------------|
| 数据存储 | 所有字段在 Order 主表 | 使用子表存储特定字段 |
| 字段复用 | 不同类型共用相同字段 | 每种类型有专属字段 |
| 扩展性 | 较低，字段冲突 | 高，易于扩展 |
| SIGN 订单 | 无专用时间字段 | 支持 start_date/end_date/execution_time |
| 创建接口 | POST /orders | POST /orders/v2 |

## 权限验证流程

当前模块实现**基于组织的权限控制**，确保数据隔离。

### 访问控制层次
1. **Django 认证层**：依赖全局中间件进行用户身份验证
2. **组织隔离层**：通过 `organization` 外键关联实现数据隔离
3. **业务逻辑层**：通过 `account` 外键关联确保业务关联

### 组织隔离机制
- **创建时**：自动关联 `request.user.organization`（在 WriteSerializer.create 中）
- **查询时**：自动过滤 `organization = request.user.organization`（在 ListParamsSerializer.get_queryset 中）
- **显示时**：返回 `organizationName` 字段（在 ListSerializer 中）
- **禁用拦截**：WriteSerializer 和 WriteV2Serializer 通过 `validate_accountId` 方法拒绝使用禁用账户（`disable_flag=True`）创建订单

### 多租户支持
- 当前系统支持多组织架构
- 每个用户只能看到自己组织的订单
- 订单通过 `organization` 关联实现组织级数据隔离

## 认证与授权区别说明

| 维度 | 认证 (Authentication) | 授权 (Authorization) |
|------|----------------------|---------------------|
| **定义** | 验证用户身份 | 验证用户权限 |
| **本模块实现** | 依赖 Django 全局认证中间件 | 通过 `organization` 外键实现组织级数据隔离 |
| **Token 管理** | 使用 User 模型的 JWT Token | 基于组织的自动权限校验 |
| **未来扩展** | OAuth2/SSO 集成 | 订单操作权限矩阵 |

## 与其他模块关系

### 依赖模块
1. **SM/Organization**：组织管理，提供组织关联和隔离
2. **BDM/Account**：订单归属账号，提供 Duolingo 凭证
3. **API/Duolingo**：提供与 Duolingo API 交互的 mapper 和 service
4. **utils/redis**：缓存服务，用于 3x_xp 任务的时效控制
5. **utils/common**：时间转换等工具函数

### 被依赖模块
- 暂无其他模块直接依赖 Order 模型

### 数据流向
```
用户请求 → View层验证 → 组织过滤（organization=request.user.organization）
                ↓
        Serializer处理 → 自动关联组织（request.user.organization）
                ↓
        Order模型创建/更新 → 创建对应子模型（v2）
                ↓
        Celery Beat定时触发
                ↓
        celery_execute_order/celery_execute_order_v2任务执行
                ↓
        调用API.Duolingo执行业务
                ↓
        更新Order和子模型状态、completed_qty
```

## 常见业务场景

### 场景 1：创建 v1 经验获取订单
```python
POST /aps/orders
{
    "accountId": 123,
    "category": "exp",
    "plannedQty": 1000,
    "planDuration": 60,
    "scheduleAt": "2026-03-08 10:00:00"
}
```

**业务逻辑**：
1. 创建订单记录，version=1
2. 自动关联当前用户的组织
3. 自动获取当前账号 exp 值存入 `before_value`
4. 等待 Celery 定时任务触发

### 场景 2：创建 v2 签到订单
```python
POST /aps/orders/v2
{
    "accountId": 123,
    "category": "sign",
    "plannedQty": 92,
    "startDate": "2026-03-15",
    "endDate": "2026-04-15",
    "executionTime": "08:00"
}
```

**业务逻辑**：
1. 创建订单记录，version=2，初始状态为 `waiting`
2. 创建 OrderSigning 子记录
3. 自动关联当前用户的组织
4. 首次到达计划执行时间时，状态从 `waiting` 转为 `doing`
5. 每天 `executionTime` 循环答题累加经验值，达到 `plannedQty` 目标后结束当日执行
6. 每日执行完毕后检查是否到达 `endDate`，是则标记订单为 `done`

### 场景 3：v1 Celery 自动执行订单
```python
# apps/APS/tasks.py:celery_execute_order
# 每分钟扫描 version=1 且 schedule_at <= 当前时间的订单
```

**执行流程**：
1. 查询状态为 `waiting/doing` 且 `schedule_at` 已到的 v1 订单
2. 根据分类调用不同执行逻辑
3. 实时更新 `completed_qty` 和 `status`

### 场景 4：v2 Celery 自动执行订单
```python
# apps/APS/tasks.py:celery_execute_order_v2
# 每分钟扫描 version=2 且状态为 waiting/doing 的订单
```

**执行流程**：
1. 查询所有 v2 版本的进行中订单
2. 根据订单类型执行不同逻辑：
   - **EXP**: 检查 schedule_at，答题获取经验
   - **GEMS**: 领取所有可用宝石奖励
   - **THREE_XP**: 检查 Redis TTL，领取三倍经验
   - **SIGN**: 检查日期范围（UTC+8）和时间（UTC+8），循环答题累加经验至 `planned_qty` 目标；首次执行时 `waiting` → `doing`，到达 `end_date` 时 → `done`
3. 更新子模型和主订单的 `completed_qty`

### 场景 5：三倍经验任务特殊处理
```python
if order_instance.category == '3x_xp':
    # 检查 Redis TTL 避免重复激活
    if redis_client.service.ttl(f"3x_xp_v2:{order_instance.id}") < 120:
        # 调用 Duolingo API 激活三倍经验
        # 设置 Redis 过期时间
```

### 场景 6：订单状态变更
```python
PATCH /aps/orders/{order_id}
{
    "status": "cancel"
}
```

**状态转换规则**（见 PatchSerializer 验证逻辑）：
- `waiting` ← `doing/error/cancel/done`
- `cancel` ← `doing/waiting`
- `done` ← `doing/waiting`

## 技术实现建议 (Django)

### 1. Serializer 验证模式
```python
class PatchSerializer(serializers.Serializer):
    def validate(self, attrs):
        order_instance = attrs['order']
        status = attrs['status']

        # 状态机验证逻辑
        if status == 'waiting' and order_instance.status not in ['doing', 'error', 'cancel', 'done']:
            raise serializers.ValidationError('订单状态不正确，不能修改为等待')
        # ...
```

### 2. v2 订单创建模式
```python
class WriteV2Serializer(serializers.Serializer):
    def create(self, validated_data):
        # 提取各类型专用字段
        plan_duration = validated_data.pop('plan_duration', None)
        schedule_at = validated_data.pop('schedule_at', None)
        # ...

        # 创建主订单
        order = Order.objects.create(**validated_data)

        # 根据类型创建子订单
        if category == Choices.OrderCategory.EXP.value:
            OrderExp.objects.create(
                order=order,
                plan_duration=plan_duration,
                schedule_at=schedule_at,
                # ...
            )
```

### 3. Celery 任务最佳实践
- 使用 `@shared_task(bind=True)` 获取任务实例
- 任务内添加异常处理，避免单个订单失败影响整体
- 使用 Redis 缓存避免高频重复操作
- v2 任务使用 `select_related` 优化查询

### 4. 查询优化
```python
# 列表查询使用 select_related 减少 N+1
queryset = Order.objects.select_related('account', 'organization').all()

# v2 任务查询包含子模型
queryset = Order.objects.filter(
    version=2,
    status__in=[Choices.OrderStatus.WAITING.value, Choices.OrderStatus.IN_PROGRESS.value]
).select_related('account', 'exp', 'gem', 'three_xp', 'signing')
```

### 5. 时间处理
- 统一使用 `django.utils.timezone.now()` 获取当前时间
- 前端展示通过 `common.to_local_time()` 转换时区
- SIGN 订单的 `execution_time`、`start_date`、`end_date` 均为 UTC+8 时区，Celery 执行时需通过 `(timezone.now() + timedelta(hours=8))` 转换后再比较

## 扩展设计策略

### 策略 1：任务执行日志表
新增 `OrderExecutionLog` 模型记录每次执行的详细信息：
- 执行时间
- 获得经验/宝石数量
- 异常信息
- Duolingo API 响应

### 策略 2：任务优先级队列
为 Order 模型添加 `priority` 字段，Celery 任务根据优先级排序执行。

### 策略 3：失败重试机制
在 Celery 任务中添加指数退避重试逻辑：
```python
@shared_task(bind=True, max_retries=3)
def celery_execute_order_v2(self):
    try:
        # 执行逻辑
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### 策略 4：v2 订单类型扩展
添加新的订单类型（如 "双倍宝石"、"连续打卡奖励"）：
1. 在 `enums.py` 中添加新的 `OrderCategory`
2. 创建对应的子模型（如 `OrderDoubleGems`）
3. 在 `WriteV2Serializer` 中添加验证逻辑
4. 在 `celery_execute_order_v2` 中添加执行逻辑

## 演进方向 (Future Evolution)

### 短期优化 (1-3 个月)
1. **完善错误处理**：添加详细的错误码和错误日志
2. **性能监控**：集成 APM 工具监控 Celery 任务执行耗时
3. **数据校验**：添加订单数量合理性校验（避免负数或超大值）

### 中期扩展 (3-6 个月)
1. **任务编排**：支持依赖任务（如签到完成后自动触发三倍经验）
2. **批量操作**：支持批量创建/取消订单
3. **报表统计**：订单执行效率分析、成功率统计
4. **通知机制**：订单完成/失败时通知用户

### 长期规划 (6-12 个月)
1. **微服务拆分**：将订单模块独立为微服务
2. **分布式调度**：使用 Kubernetes CronJob 替代 Celery Beat
3. **智能调度**：基于历史数据预测最佳执行时间
4. **跨组织订单**：支持组织间订单协作与共享

## 模块特有名词解释

| 名词 | 定位 | 快速索引 |
|------|------|---------|
| **planned_qty** | 计划数量，经验/宝石任务的目标值 | `models.Order.planned_qty` |
| **plan_duration** | 计划持续时间，任务分批执行的次数 | `models.Order.plan_duration` |
| **before_value** | 初始值，用于计算任务执行后的增量 | `models.Order.before_value` |
| **3x_xp** | 三倍经验，Duolingo 经验加成道具 | `enums.Choices.category` |
| **schedule_at** | 计划时间，Celery 任务调度依据 | `models.Order.schedule_at` |
| **organization** | 组织关联，实现多租户数据隔离 | `models.Order.organization` |
| **organizationName** | 组织名称，用于前端显示 | `serializers.ListSerializer.organizationName` |
| **celery_execute_order** | v1 核心异步任务，扫描并执行到期订单 | `tasks.py` |
| **celery_execute_order_v2** | v2 核心异步任务，扫描并执行 v2 订单 | `tasks.py` |
| **category** | 业务分类，区分不同自动化任务类型 | `enums.Choices.category` |
| **doing** | 进行中状态，订单正在执行 | `enums.Choices.status` |
| **version** | 订单版本号，v1=1, v2=2 | `models.Order.version` |
| **OrderExp** | v2 经验订单子模型 | `models.OrderExp` |
| **OrderSigning** | v2 签到订单子模型 | `models.OrderSigning` |
| **execution_time** | 签到订单的执行时间（HH:MM） | `models.OrderSigning.execution_time` |
| **accumulated_exp** | SIGN 任务局部变量，累加当日答题获得经验值 | `tasks._execute_sign_order_v2` |

## 关键文件索引

| 文件路径 | 职责 |
|---------|------|
| `apps/APS/order/models.py` | Order 数据模型定义（含 v2 子模型） |
| `apps/APS/order/enums.py` | 状态和分类枚举 |
| `apps/APS/order/views.py` | REST API 视图（ListView/DetailView/ListV2View） |
| `apps/APS/order/serializers.py` | 数据序列化与验证（含 WriteV2Serializer） |
| `apps/APS/order/tasks.py` | Celery 异步任务定义（含 v2 任务） |
| `apps/APS/urls.py` | URL 路由配置 |

## 视图说明

### ListView - 订单列表视图
- **GET**: 获取订单列表，支持分页和多条件筛选
- **POST**: 创建新订单 (v1)

### ListV2View - 多版本兼容订单列表/创建视图
- **GET**: 获取所有版本订单列表，使用 `ListV2Serializer`（含 `beforeValue`、`scheduleAt` 顶层字段）
- **POST**: 创建 v2 版本订单

### DetailV2View - v2 订单详情视图
- **GET**: 获取 v2 版本订单详情，使用 DetailV2Serializer 返回结构化数据

### DetailView - 订单详情视图
- **GET**: 获取订单详情，返回结构化的四类数据
- **PATCH**: 更新订单状态

### DetailSerializer 响应结构
订单详情接口返回的数据按四个分类组织：

| 分类 | 字段 | 说明 |
|------|------|------|
| document | id, code, scheduleAt, status, category | 文档类字段 |
| progressData | plannedQty, beforeValue, completedQty, planDuration | 进度数据字段 |
| relations | account, customer, organization | 关联信息字段 |
| recentLogs | 最近 10 条执行日志（order_id/orderCode/status/resultValue 等） | 日志数据字段 |
| others | createdAt, updatedAt | 其他字段 |

---

**最后更新**: 2026-03-30
