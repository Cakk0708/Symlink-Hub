# PM 项目日志模块 (PM Project Log)

## 模块定位

PM 项目日志模块是项目管理系统的**操作审计与进展跟踪中心**，负责记录项目生命周期内的所有关键操作和进展汇报。

**核心价值**：
- 提供完整的操作审计链路
- 支持项目进展的可追溯性
- 为项目评价提供数据基础

## 模块职责边界

### 负责范围
- ✅ 项目操作日志记录（type=0）
- ✅ 项目进展汇报记录（type=1）
- ✅ 项目评价记录（type=2）
- ✅ 智能时间显示（刚刚、X分钟前、X小时前、X天前）
- ✅ 内容详情 JSON 字段管理

### 不负责范围
- ❌ 项目状态变更（由 PM/project 模块负责）
- ❌ 节点操作日志（由 PM/nodelist 模块负责）
- ❌ 审批流程日志（由 SM/approval 模块负责）
- ❌ 飞书消息推送（由 SM/message 模块负责）

## 核心数据模型

### Log 模型

**表名**：`PM_log_list`

**字段结构**：
```
Log
├── id                      # 主键
├── content                 # 日志内容（varchar 1000）
├── project                 # 关联项目（外键 → PM.Project_List）
├── operator                # 操作人（外键 → SM.User，nullable）
├── create_time             # 创建时间（auto_now_add）
├── type                    # 日志类型（0=操作记录, 1=进展汇报, 2=评价记录）
└── content_detail          # 内容详情（JSONField，nullable）
```

**日志类型枚举**：
| 值 | 名称 | 说明 |
|---|---|---|
| 0 | 操作记录 | 项目状态变更、节点操作等 |
| 1 | 进展汇报 | 项目进展更新汇报 |
| 2 | 评价记录 | 项目评价相关记录 |

## 权限验证流程

### 认证层
- 使用 `IsAuthenticated` 权限类
- 通过 `UserHelper.setup_request_userinfo(request)` 获取用户上下文

### 授权层
- **读取权限**：项目成员可查看项目日志
- **创建权限**：项目参与者可创建进展汇报
- **操作权限**：仅记录操作，不涉及额外权限控制

### 特殊逻辑
- **评价记录隐私**：type=2 的记录仅对超管显示详情
- **操作人脱敏**：匿名操作显示默认头像和昵称

## 认证与授权区别说明

| 维度 | 认证 (Authentication) | 授权 (Authorization) |
|---|---|---|
| **问题** | "你是谁？" | "你能做什么？" |
| **实现** | `IsAuthenticated` 权限类 | 项目成员关系验证 |
| **数据源** | `SM.User` 模型 | `PM.Project_List.participants` |
| **本模块** | Django REST Framework 处理 | 通过 userinfo 上下文传递 |

## 与其他模块关系

### 依赖关系
```
PM/log (日志模块)
├── 依赖 → PM.Project_List      # 项目主体
├── 依赖 → SM.User              # 操作人
├── 被依赖 → PM/project         # 项目详情页展示日志
├── 被依赖 → PM/nodelist        # 节点操作记录
└── 被依赖 → PM/evaluation      # 评价记录查询
```

### 数据流向
1. **操作触发**：各业务模块（project、nodelist等）触发操作
2. **日志创建**：调用 `common.projectInsertPeratorLog()` 创建日志
3. **日志查询**：前端通过日志模块接口获取日志列表
4. **时间展示**：智能时间显示在前端或序列化器中处理

## 常见业务场景

### 场景1：项目进展汇报
**用户操作**：项目成员更新项目进展
**系统流程**：
1. 用户提交进展内容
2. `ProgressCreateSerializer` 验证数据
3. 调用 `common.projectInsertPeratorLog(_type=1)` 创建日志
4. 返回创建成功响应

### 场景2：查看项目日志
**用户操作**：用户进入项目详情页查看操作历史
**系统流程**：
1. 前端请求日志列表（携带 projectId、pageNum、pageSize）
2. `ParamsSerializer` 验证并处理分页参数
3. `LogListView` 查询该项目的日志记录
4. `LogListSerializer` 序列化数据
5. 应用智能时间显示逻辑
6. 返回格式化后的日志列表（items + pagination）

### 场景3：操作审计
**用户操作**：管理员查看特定时间段的操作记录
**系统流程**：
1. 管理员发起审计查询
2. 过滤 type=0 的操作记录
3. 显示完整的操作人信息
4. 可追溯操作链路

## 技术实现建议（Django）

### 序列化器规范

**基础序列化器**：`LogListSerializer`
```python
class LogListSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='create_time')
    createdBy = serializers.SerializerMethodField()
    displayTime = serializers.SerializerMethodField()

    def get_displayTime(self, obj):
        # 智能时间显示逻辑
        pass
```

**参数序列化器**：`ParamsSerializer`
```python
class ParamsSerializer(serializers.Serializer):
    """日志列表参数序列化器，统一处理筛选、分页等参数"""
    projectId = serializers.IntegerField(required=False, default=None)
    type = serializers.IntegerField(required=False, default=None)
    pageNum = serializers.IntegerField(required=False, default=1, min_value=1)
    pageSize = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100)

    def get_paginated_queryset(self, queryset):
        # 处理筛选、排序、分页
        # 返回 (paginated_queryset, pagination_dict)
        pass
```

**创建序列化器**：`ProgressCreateSerializer`
```python
class ProgressCreateSerializer(serializers.Serializer):
    projectId = serializers.IntegerField(source='project_id')
    content = serializers.CharField(max_length=1000)

    def validate_project_id(self, value):
        # 验证项目是否存在
        pass
```

### 视图层规范

**标准 APIView 结构**：
```python
class ProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        self.code = kwargs.get('code', None)
        self.action = kwargs.get('action', None)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # 获取列表
        pass

    def post(self, request, *args, **kwargs):
        # 创建记录
        pass
```

### 返回结构规范（camelCase）

**成功响应（列表）**：
```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 123,
        "content": "日志内容",
        "createdAt": "2024-01-10 14:30:00",
        "displayTime": "2天前",
        "createdBy": {
          "id": 456,
          "avatar": "avatar_url",
          "nickname": "用户名"
        }
      }
    ],
    "pagination": {
      "pageNum": 1,
      "pageSize": 10,
      "total": 100,
      "totalPages": 10
    }
  }
}
```

**错误响应**：
```json
{
  "msg": "数据验证失败",
  "errors": {
    "projectId": ["该字段是必填的"]
  }
}
```

## 扩展设计策略

### 水平扩展
- **分页支持**：使用 pageNum/pageSize 实现分页（通过 ParamsSerializer 统一处理）
- **索引优化**：在 project_id、type、create_time 上建立复合索引

### 垂直扩展
- **内容分类**：通过 content_detail JSON 字段存储结构化数据
- **多语言支持**：content 字段可扩展为多语言结构

### 功能扩展点
1. **日志归档**：定期归档历史日志到归档表
2. **日志导出**：支持导出为 Excel/PDF 格式
3. **日志搜索**：全文检索日志内容
4. **日志统计**：按类型、时间统计日志分布

## 演进方向（Future Evolution）

### 短期（1-3个月）
- [ ] 增加日志标签功能
- [ ] 支持日志附件上传
- [ ] 实现日志全文搜索

### 中期（3-6个月）
- [ ] 日志数据可视化
- [ ] 操作热力图分析
- [ ] 异常操作告警

### 长期（6个月以上）
- [ ] AI 驱动的操作建议
- [ ] 自动生成项目日报
- [ ] 日志数据挖掘与趋势预测

## 模块特有名词索引

| 名词 | 说明 | 关联 |
|---|---|---|
| **进展汇报** | type=1 的日志记录，记录项目进展更新 | ProgressView, ProgressCreateSerializer |
| **操作记录** | type=0 的日志记录，记录项目操作历史 | LogListView |
| **评价记录** | type=2 的日志记录，记录项目评价，内容对普通用户隐藏 | LogListSerializer.get_content() |
| **displayTime** | 智能时间显示字段，根据时间差显示友好格式 | LogListSerializer.get_displayTime() |
| **content_detail** | JSON 字段，存储日志的详细信息 | Log.content_detail |
| **ParamsSerializer** | 参数序列化器，统一处理筛选、分页等参数 | LogListView, ProgressView |
| **projectInsertPeratorLog** | 创建日志的公共方法 | assists/common.py |
| **pageNum/pageSize** | 统一分页参数，替代旧的 limit/skip | ParamsSerializer |
| **items/pagination** | 统一响应结构，替代旧的 list/count | 全局规范 |

## URL 路由

```
/pm/log/                    # 日志模块基础路径
├── GET  /                  # 获取日志列表（LogListView）
├── POST /                  # 创建日志（预留）
└── /progress               # 进展汇报接口
    ├── GET  /              # 获取进展列表（ProgressView.get）
    └── POST /              # 创建进展（ProgressView.post）
```

## 快速参考

### 创建进展记录
```python
# 调用公共方法
from assists import common
log_id = common.projectInsertPeratorLog(
    project_id=project_id,
    content=content,
    user_id=user_id,
    _type=1  # 1=进展汇报
)
```

### 查询项目日志
```python
from apps.PM.log.models import Log

# 查询某项目的所有日志
logs = Log.objects.filter(project_id=project_id)

# 查询某项目的进展汇报
progress_logs = Log.objects.filter(project_id=project_id, type=1)

# 分页查询（使用 pageNum/pageSize）
page_num = 1
page_size = 10
start = (page_num - 1) * page_size
end = start + page_size
logs = Log.objects.filter(project_id=project_id)[start:end]
```