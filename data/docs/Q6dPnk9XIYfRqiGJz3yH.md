# PM 项目关注者模块 (PM Project Follower Module)

## 模块定位

PM/project/follower 是项目管理系统的关注关系管理模块，负责维护用户对项目的关注关系。这是一个独立的多对多关系表模块，从原有的 `Project_List.followers` JSONField 字段迁移而来，提供更规范的关系管理和批量操作能力。

## 核心职责

1. **关注关系管理**：维护用户与项目的关注关系
2. **关注状态切换**：支持用户点击切换关注/取消关注状态
3. **批量操作**：支持批量添加/删除关注者
4. **关系验证**：防止重复关注、验证删除权限
5. **数据迁移**：从 JSONField 迁移到独立关系表

## 模块边界

### 包含的功能
- 切换关注状态 (`POST /pm/project/{id}/follower`) - 支持关注/取消关注自动切换
- 批量删除关注者 (`DELETE /pm/project/{id}/follower`)

### 不包含的功能
- 项目详情查询（PM/project）
- 用户权限验证（PM/authority）
- 项目列表筛选（type=FLW 筛选逻辑在 PM/project/views.py 中）

## 核心数据模型

### ProjectFollower（项目关注者）

**文件位置**：`apps/PM/project/follower/models.py`

```python
class ProjectFollower(models.Model):
    """项目关注者模型 - 通过独立的中间表实现项目与用户的多对多关系"""

    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(
        Project_List,
        on_delete=models.CASCADE,
        related_name='project_followers',
        verbose_name='项目'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_projects',
        verbose_name='关注者'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='关注时间'
    )

    class Meta:
        db_table = 'PM_project_follower'
        unique_together = [['project', 'user']]  # 防止重复关注
        ordering = ['-created_at']
```

**设计要点**：
- 使用独立中间表而非 ManyToManyField，便于扩展关注关系属性
- `unique_together` 约束防止同一用户重复关注同一项目
- `created_at` 记录关注时间，支持按时间排序
- `project_followers` 反向关系名，便于查询项目的所有关注者
- `following_projects` 反向关系名，便于查询用户关注的所有项目

## 序列化器设计

### AddFollowerWriteSerializer（添加关注者）

**文件位置**：`apps/PM/project/follower/serializers.py`

```python
class AddFollowerWriteSerializer(serializers.Serializer):
    """添加关注者写入序列化器"""

    projectId = serializers.PrimaryKeyRelatedField(
        source='project',
        queryset=Project_List.objects.all(),
        required=True,
        error_messages=serializer_func.error_data
    )

    userId = serializers.PrimaryKeyRelatedField(
        source='user',
        queryset=User.objects.all(),
        required=True,
        error_messages=serializer_func.error_data
    )

    def validate(self, attrs):
        """验证用户是否已经关注该项目"""
        if ProjectFollower.objects.filter(
            project=attrs['project'],
            user=attrs['user']
        ).exists():
            raise ValidationError('该用户已关注此项目')
        return attrs
```

**设计要点**：
- 使用 `PrimaryKeyRelatedField` 自动验证项目和用户是否存在
- `source` 参数实现驼峰命名到下划线命名的映射
- 在 `validate()` 方法中检查是否已存在关注关系

### RemoveFollowerWriteSerializer（删除关注者）

```python
class RemoveFollowerWriteSerializer(serializers.Serializer):
    """移除关注者写入序列化器 - 支持批量删除"""

    projectId = serializers.PrimaryKeyRelatedField(
        source='project',
        queryset=Project_List.objects.all(),
        required=True
    )

    ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all()
        ),
        required=True,
        error_messages={'required': 'ids 不能为空'}
    )

    def validate(self, attrs):
        """验证用户是否关注该项目"""
        existing_followers = ProjectFollower.objects.filter(
            project=attrs['project'],
            user__in=attrs['ids']
        ).values_list('user_id', flat=True)

        not_following = set(u.id for u in attrs['ids']) - set(existing_followers)
        if not_following:
            raise ValidationError(f'用户 {list(not_following)} 未关注此项目')
        return attrs

    def execute_delete(self):
        """执行批量删除"""
        deleted_count = ProjectFollower.objects.filter(
            project=self.validated_data['project'],
            user__in=self.validated_data['ids']
        ).delete()[0]
        return deleted_count
```

**设计要点**：
- 使用 `ListField` + `PrimaryKeyRelatedField` 实现批量删除
- `execute_delete()` 方法而非 `save()`，符合删除操作语义
- 返回删除数量，便于前端确认操作结果
- 验证所有用户都已关注该项目

## 视图设计

### ProjectFollowerView

**文件位置**：`apps/PM/project/follower/views.py`

```python
class ProjectFollowerView(views.APIView):
    """项目关注者视图 - 提供关注切换和批量删除功能"""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """切换关注状态（关注/取消关注）"""
        project_id = kwargs.get('id')
        user_id = request.data.get('userId')

        if not user_id:
            return JsonResponse({
                'msg': '参数错误',
                'data': {'userId': '该字段不能为空'}
            }, status=400)

        # 检查是否已存在关注记录
        follower = ProjectFollower.objects.filter(
            project_id=project_id,
            user_id=user_id
        ).first()

        if follower:
            # 已关注，执行取消关注
            follower.delete()
            is_following = False
            msg = '取消关注成功'
        else:
            # 未关注，执行添加关注
            try:
                follower = ProjectFollower.objects.create(
                    project_id=project_id,
                    user_id=user_id
                )
                is_following = True
                msg = '关注成功'
            except Exception:
                return JsonResponse({
                    'msg': '操作失败，请稍后重试'
                }, status=500)

        return JsonResponse({
            'msg': msg,
            'data': {
                'isFollowing': is_following
            }
        })

    def delete(self, request, *args, **kwargs):
        """批量删除关注者"""
        project_id = kwargs.get('id')

        data = request.data.copy()
        data['projectId'] = project_id

        serializer = RemoveFollowerWriteSerializer(
            data=data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return JsonResponse({
                'msg': '参数错误',
                'data': serializer.errors
            }, status=400)

        deleted_count = serializer.execute_delete()

        return JsonResponse({
            'msg': 'success',
            'data': {
                'deletedCount': deleted_count
            }
        })
```

**设计要点**：
- `post()` 方法实现关注状态切换逻辑，而非单纯的添加
- 直接操作模型，不使用序列化器（简化逻辑）
- 返回 `isFollowing` 布尔值表示当前关注状态
- 使用 `unique_together` 约束防止并发重复关注

## API 端点

### 切换关注状态（关注/取消关注）
```http
POST /pm/project/{id}/follower
Content-Type: application/json

{
  "userId": 456
}

# 关注成功响应
Response 200:
{
  "msg": "关注成功",
  "data": {
    "isFollowing": true
  }
}

# 取消关注响应
Response 200:
{
  "msg": "取消关注成功",
  "data": {
    "isFollowing": false
  }
}

Error 400:
{
  "msg": "参数错误",
  "data": {
    "userId": "该字段不能为空"
  }
}
```

**逻辑说明**：
- 如果用户未关注该项目，则添加关注
- 如果用户已关注该项目，则取消关注
- 返回操作后的当前关注状态 (`isFollowing`)

### 删除关注者（批量）
```http
DELETE /pm/project/{id}/follower
Content-Type: application/json

{
  "projectId": 123,
  "ids": [456, 789]
}

Response 200:
{
  "msg": "success",
  "data": {
    "deletedCount": 2
  }
}

Error 400:
{
  "msg": "参数错误",
  "data": "用户 [456] 未关注此项目"
}
```

## 与其他模块关系

### 依赖的模块
```
apps.PM.project.models
  └── Project_List - 项目模型

apps.SM.models
  └── User - 用户模型

assists.serializer
  └── error_data - 统一错误消息
```

### 被依赖的模块
```
apps.PM.project.serializers
  └── DetailSerializer.get_followers() - 从 ProjectFollower 查询关注者列表

apps.PM.project.views
  └── ListView.type=FLW - 筛选用户关注的项目
```

## 数据迁移历史

### 从 JSONField 迁移到独立表

**迁移前**（Project_List 模型）：
```python
followers = models.JSONField()  # 存储用户ID列表
```

**迁移后**（独立表）：
```python
# ProjectFollower 独立模型
# DetailSerializer.get_followers() 改为：
follower_records = ProjectFollower.objects.filter(project=obj)
return [self._construct_user(user_instance=record.user)
        for record in follower_records]
```

**迁移优势**：
1. 规范的关系管理（外键约束）
2. 支持关注时间记录
3. 便于扩展关注关系属性（如关注原因、关注来源）
4. 批量操作性能更好
5. 查询更直观（ORM 关系查询）

## 常见业务场景

### 场景1：用户点击关注按钮（切换关注状态）
```
1. 前端调用 POST /pm/project/{id}/follower
2. 传入 userId（当前用户ID）
3. 后端检查是否已关注该项目
4. 未关注 → 创建记录 → 返回 isFollowing: true
5. 已关注 → 删除记录 → 返回 isFollowing: false
6. 前端根据 isFollowing 更新按钮状态
```

### 场景2：批量移除关注者
```
1. 前端调用 DELETE /pm/project/{id}/follower
2. 传入 projectId（从 URL 注入）和用户ID列表 ids
3. 序列化器验证所有用户是否都已关注该项目
4. 执行批量删除
5. 返回删除数量
```

### 场景3：项目详情显示关注者列表
```
1. DetailSerializer.get_followers() 方法
2. 查询 ProjectFollower.objects.filter(project=project)
3. 序列化用户信息（id, nickname, avatar）
4. 返回关注者列表
```

### 场景4：筛选用户关注的项目
```
1. ListView.type=FLW 筛选逻辑
2. 查询 ProjectFollower.objects.filter(user_id=user.id)
3. 获取项目ID列表
4. 筛选状态为进行中或变更中的项目
```

## 技术实现要点

### Django ORM 使用
```python
# 查询项目的所有关注者
followers = ProjectFollower.objects.filter(
    project_id=project_id
).select_related('user').order_by('-created_at')

# 查询用户关注的所有项目
projects = ProjectFollower.objects.filter(
    user_id=user_id
).select_related('project')

# 批量删除关注关系
deleted_count = ProjectFollower.objects.filter(
    project_id=project_id,
    user__in=user_ids
).delete()[0]
```

### 序列化器最佳实践
```python
# 1. 使用 PrimaryKeyRelatedField 自动验证存在性
projectId = serializers.PrimaryKeyRelatedField(
    source='project',
    queryset=Project_List.objects.all()
)

# 2. 使用 source 实现命名映射
# userId -> user, projectId -> project

# 3. 批量操作使用 ListField
ids = serializers.ListField(
    child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
)

# 4. 删除操作使用 execute_xxx() 方法
def execute_delete(self):
    # 执行删除逻辑
    return deleted_count
```

### 视图参数注入模式
```python
# URL 中的参数注入到请求数据中
def post(self, request, *args, **kwargs):
    project_id = kwargs.get('id')

    data = request.data.copy()
    data['projectId'] = project_id

    serializer = AddFollowerWriteSerializer(
        data=data,
        context={'request': request}
    )
```

## 特殊名词索引

当用户提到以下名词时，应定位到此模块：

- **项目关注者**、**ProjectFollower** → PM/project/follower
- **关注项目**、**取消关注** → PM/project/follower
- **followers** → PM/project/follower (从 Project_List 模型迁移)
- **关注关系**、**关注列表** → PM/project/follower
- **type=FLW** → PM/project/views.py (使用 ProjectFollower 筛选)

## 扩展设计策略

### 当前架构优势
1. **规范化关系**：使用独立中间表替代 JSONField
2. **外键约束**：数据库层面的引用完整性
3. **可扩展性**：便于添加关注关系属性（关注原因、来源等）
4. **批量操作**：支持高效的批量添加/删除
5. **查询优化**：使用 select_related 优化关联查询

### 未来演进方向
1. **关注通知**：用户关注项目后发送通知给项目负责人
2. **关注原因**：添加关注原因字段（可选）
3. **关注来源**：记录关注来源（主动关注/邀请关注）
4. **关注权限**：区分公开项目和私密项目的关注权限
5. **关注统计**：项目关注数统计、热门项目排行
6. **关注推荐**：基于用户行为推荐相关项目
7. **关注分组**：支持关注分组（如"我参与的"、"我关注的"）

## 编码规范

### 模型命名
- 表名：`PM_project_follower`（app_label + model）
- 字段名：`created_at`（统一使用 created_at 而非 create_time）
- 反向关系：`project_followers`、`following_projects`

### 序列化器命名
- 写入序列化器：`AddFollowerWriteSerializer`、`RemoveFollowerWriteSerializer`
- 外部字段：驼峰命名（`projectId`、`userId`）
- 内部字段：下划线命名（通过 `source` 映射）

### 视图规范
- 返回结构：`{"msg": "success", "data": {...}}`
- 错误响应：`{"msg": "参数错误", "data": serializer.errors}`
- URL 参数注入：将 `{id}` 注入为 `projectId`

### 注释规范
- 模块顶部：包含 Module、Description、Author
- 类注释：简洁描述类的用途
- 方法注释：使用 docstring 描述参数和返回值

## 变更记录

### 2026-03-16
- **POST 接口重构**：从单纯的"添加关注"改为"切换关注状态"
  - 响应格式从用户信息改为 `isFollowing` 布尔值
  - 响应消息改为动态的"关注成功"/"取消关注成功"
  - 直接操作模型，移除对 `AddFollowerWriteSerializer` 的依赖
  - 简化前端交互，无需维护关注状态
