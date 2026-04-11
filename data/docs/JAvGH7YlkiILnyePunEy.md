# PM 项目节点笔记模块

## 模块定位

节点笔记 (NodeNote) 是 PM 项目管理系统中 nodelist 模块的子功能，为项目节点提供轻量级文本记录能力。该模块采用简洁的单表关联设计，允许用户为任意节点添加备注、说明或临时记录。

**所属层级**：`apps/PM/nodelist/note/`

## 触发条件

当用户提到以下任一概念时，应激活此技能：

- "节点笔记"、"NodeNote"、"笔记功能"
- "pm/node/{id}/note" 接口
- 节点详情中的 `features.note` 字段
- "created_by"、"created_at"、"content" 与节点相关的笔记操作

## 核心数据模型

### NodeNote 模型

```python
class NodeNote(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField(verbose_name='笔记内容')
    created_by = models.ForeignKey('SM.User', on_delete=models.CASCADE, related_name='created_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    node = models.ForeignKey('PM.Project_Node', on_delete=models.CASCADE, related_name='notes')
```

**关系说明**：
- 一个节点 (`Project_Node`) 可以有多条笔记 (OneToMany)
- 一条笔记只能属于一个节点
- `related_name='notes'` 使节点可通过 `node.notes.all()` 查询所有笔记

**数据库表**：`PM_node_note`

## API 接口

### 1. 添加笔记

**接口**：`POST /pm/node/{id}/note`

**请求参数**：
```json
{
  "content": "笔记内容"
}
```

**返回结构**（camelCase）：
```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "content": "笔记内容",
    "createdByName": "张三",
    "createdByAvatar": "https://...",
    "createdAt": "2026-03-09 11:23:45"
  }
}
```

### 2. 获取节点详情（包含最新笔记）

**接口**：`GET /pm/node/{id}`

**🆕 Since 2026-03-09**：笔记信息已迁移到 `features` 字段中。

**返回结构**：
```json
{
  "id": 123,
  "name": "节点名称",
  "features": {
    "review": {...},
    "deliverable": {...},
    "submitTest": false,
    "note": {
      "id": 1,
      "content": "最新笔记内容",
      "createdByName": "张三",
      "createdByAvatar": "https://...",
      "createdAt": "2026-03-09 11:23:45"
    }
  }
}
```

**⚠️ Deprecated**：独立 `note` 字段已废弃，请使用 `features.note` 访问。

**规则**：仅返回最新的一条笔记（按 `created_at` 倒序）

### 实现细节

在 `apps/PM/nodelist/serializers.py` 的 `ReadSerializer` 中：

```python
def _get_note_info(self, obj):
    """
    获取节点最新的一条笔记信息
    """
    from apps.PM.nodelist.note.models import NodeNote

    latest_note = obj.notes.order_by('-created_at').first()
    if latest_note:
        serializer = NodeNoteReadSerializer(latest_note)
        return serializer.data
    return None
```

## 技术实现规范

### 命名规范

- **模型字段**：`created_at`（时间）、`created_by`（用户）、`content`（内容）
- **API 返回**：camelCase 格式（`createdAt`、`createdByName`、`createdByAvatar`）
- **数据库表名**：`PM_node_note`（app_label + model）

### 认证与授权

- **认证**：使用 `IsAuthenticated` 权限类
- **用户获取**：直接使用 `request.user`（不再使用 `UserHelper`）
- **日志记录**：通过 `common.projectInsertPeratorLog()` 记录操作

### 序列化器设计

**创建序列化器** (`NodeNoteCreateSerializer`)：
- 继承 `serializers.Serializer`（非 ModelSerializer）
- 验证 `content` 非空
- 在 `create()` 方法中关联节点和用户

**读取序列化器** (`NodeNoteReadSerializer`)：
- 继承 `serializers.ModelSerializer`
- 使用 `source` 参数映射字段
- 返回 camelCase 格式字段名

## 模块边界与职责

### 职责范围

- ✅ 创建节点笔记
- ✅ 返回节点最新笔记（通过节点详情接口）
- ✅ 笔记内容验证

### 职责边界

- ❌ 不负责笔记编辑/删除（未来扩展）
- ❌ 不负责笔记分享/权限
- ❌ 不涉及富文本或附件

## 与其他模块关系

| 依赖模块 | 关系类型 | 说明 |
|---------|---------|------|
| `PM.Project_Node` | ForeignKey | 笔记所属的节点 |
| `SM.User` | ForeignKey | 笔记创建者 |
| `PM.nodelist.serializers` | 调用 | 节点详情序列化器集成 note 到 features 中 |

## 文件结构

```
apps/PM/nodelist/note/
├── __init__.py
├── models.py           # NodeNote 模型
├── serializers.py      # 创建/读取序列化器
├── views.py            # NodeNoteView 视图
└── urls.py             # 路由定义（已合并到父模块）
```

## 常见业务场景

1. **节点备注**：项目负责人为节点添加说明或注意事项
2. **问题记录**：记录节点执行过程中遇到的问题
3. **临时信息**：存储节点的临时沟通信息

## 扩展设计策略

### 未来演进方向

1. **笔记管理**：
   - 编辑/删除笔记
   - 笔记历史版本

2. **功能增强**：
   - 支持富文本
   - 支持附件上传
   - 笔记标签/分类

3. **协作功能**：
   - @提及其他用户
   - 笔记评论
   - 笔记分享

### 技术债务

- 当前无删除/编辑接口，数据不可变
- 无笔记内容长度限制
- 无敏感词过滤

## 开发注意事项

1. **URL 路由**：note 子模块的 URL 已直接集成到 `apps/PM/nodelist/urls.py`，无需单独 include
2. **时间格式**：使用 `to_local_time()` 工具函数格式化时间
3. **错误处理**：统一的错误消息格式 `{'msg': '错误描述'}`
4. **🆕 字段位置**：笔记信息通过 `features.note` 访问，不再作为独立字段返回
