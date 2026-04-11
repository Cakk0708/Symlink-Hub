# project-detail-follower

PMS 项目详情页 - 关注人模块专家

## 模块定位

关注人模块是 PMS 项目详情页"基本信息"标签页中的"相关人员"区域的核心功能，负责管理项目关注者（followers）的添加与删除。

**所属页面**: `pagesProject/components/basic-info.vue`

**触发关键词**: 关注人、follower、添加关注、删除关注、关注者管理

## 模块职责边界

### 核心职责
- 管理项目关注者列表的增删操作
- 同步当前用户的关注状态到全局状态
- 触发项目列表页的状态更新事件

### 边界界定
- **包含**: 关注者的添加、删除操作
- **不包含**: 关注人列表的数据获取（由项目详情接口 `GET /pm/project/{id}` 返回）
- **不包含**: 用户列表的获取（从 localStorage 的 `betaUserList` 读取）

## 核心数据模型

### 前端数据结构

```javascript
// formData.follower
{
  list: [],    // 可选用户列表，从 localStorage 的 betaUserList 读取
  value: []    // 已选关注者的 ID 数组
}
```

### 后端接口数据结构

**项目详情接口返回** (`GET /pm/project/{id}`):
```json
{
  "data": {
    "followers": [
      {
        "id": 2,
        "open_id": "ou_xxx",
        "nickname": "张三",
        "avatar": "https://..."
      }
    ]
  }
}
```

## API 规范

### 1. 添加关注者

**接口**: `POST /pm/projects/{ID}/follower`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "userId": 2
}
```

**响应示例**:
```json
{
  "msg": "success",
  "data": {
    "id": 2,
    "nickname": "张三"
  }
}
```

### 2. 删除关注者

**接口**: `DELETE /pm/projects/{ID}/follower`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "ids": [2]
}
```

**响应示例**:
```json
{
  "msg": "success",
  "data": null
}
```

## 权限验证

| 权限码 | 功能 |
|--------|------|
| 1006 | 编辑项目关注人 |

**权限检查位置**: `basic-info.vue:190`
```vue
:disabled="!permission(1006, 'project')"
```

## 核心方法解析

### handleFollow(user_id, is_add)

**位置**: `basic-info.vue:673-693`

**功能**: 根据操作类型调用对应的添加/删除接口

```javascript
async handleFollow(user_id, is_add) {
  if (is_add) {
    // 添加关注者
    await this.$util.request({
      url: `pm/projects/${this.projectId}/follower`,
      data: { userId: user_id },
      method: 'POST',
      contentType: 'json'
    })
  } else {
    // 删除关注者
    await this.$util.request({
      url: `pm/projects/${this.projectId}/follower`,
      data: { ids: [user_id] },
      method: 'DELETE',
      contentType: 'json'
    })
  }
}
```

### changeFollowPeople(val, item)

**位置**: `basic-info.vue:637-644`

**功能**: 选择器变化回调，处理关注状态的变更

```javascript
changeFollowPeople(val, item) {
  let result = this.formData.follower.value.some(follower => follower == item.id)
  this.handleFollow(item.id, result)
  if (item.id == this.userinfo.id) {
    this.$emit('setFollowStateEven', result)
    if (!result) uni.$emit('changeProListEven', { project_id: this.projectId, type: 'unFollow' })
  }
}
```

## 与其他模块关系

### 依赖模块
| 模块 | 依赖关系 |
|------|----------|
| 项目详情接口 | 获取 followers 数据 |
| 全局状态 (Vuex) | 用户信息、权限数据 |
| 项目列表页 | 通过 `uni.$emit` 同步状态 |

### 事件通信
```javascript
// 向父组件发送关注状态变化
this.$emit('setFollowStateEven', result)

// 通知项目列表页更新
uni.$emit('changeProListEven', { project_id: this.projectId, type: 'unFollow' })
```

## 常见业务场景

### 场景 1: 用户关注项目
1. 用户在关注人下拉框中选择自己
2. `changeFollowPeople` 检测到新增
3. 调用 `POST /pm/projects/{ID}/follower`
4. 更新本地关注状态

### 场景 2: 用户取消关注
1. 用户在关注人下拉框中取消选择自己
2. `changeFollowPeople` 检测到移除
3. 调用 `DELETE /pm/projects/{ID}/follower`
4. 触发项目列表页移除该项目

### 场景 3: 项目负责人变更
当项目负责人变更为非当前用户，且当前用户是创建者时，自动将当前用户添加为关注者。

**位置**: `basic-info.vue:654-660`

## UI 组件配置

```vue
<zxz-uni-data-select
  ref="ref_follower"
  :disabled="!permission(1006, 'project')"
  :multiple="true"
  :collapseTags="true"
  :collapseTagsNum="2"
  dataKey="nickname"
  dataValue="id"
  v-model="formData.follower.value"
  :localdata="formData.follower.list"
  @change="changeFollowPeople"
/>
```

**关键配置**:
- `dataValue="id"`: 使用用户 ID 作为值（非 open_id）
- `:multiple="true"`: 支持多选
- `:collapseTags="true"`: 超过 2 个时折叠显示

## 关键名词索引

| 名词 | 说明 |
|------|------|
| follower | 关注人 |
| userId | 用户 ID（后端接口使用） |
| open_id | 飞书用户标识（前端历史遗留，现已弃用） |
| setFollowStateEven | 关注状态变化事件 |
| changeProListEven | 项目列表更新事件 |