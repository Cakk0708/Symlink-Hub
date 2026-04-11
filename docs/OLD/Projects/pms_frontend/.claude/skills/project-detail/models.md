# PMS 项目详情模块 - 数据模型定义

## 项目详情接口响应结构

### 核心响应对象 (ProjectDetailResponse)

```typescript
interface ProjectDetailResponse {
  msg: string;
  data: {
    // 项目基本信息
    id: number;
    name: string;
    create_time: string;
    deadline_time: string;
    complete_time: string | false;
    last_change_time: string | false;
    content: string;
    state: ProjectState;           // 项目状态码
    place_order_flag: boolean;     // 是否下单
    is_overdue: boolean;           // 是否逾期
    is_archive: boolean;           // 是否归档

    // 人员信息
    creator: Creator;              // 创建者
    owner: Owner;                  // 项目负责人（注意使用 id 字段）
    followers: Follower[];         // 关注人列表

    // 客户信息
    customer: Customer;

    // 节点信息
    nodes: Nodes;

    // 评价相关
    evaluationAvailable: boolean;
    evaluationVisible: boolean;
    evaluationStatus: EvaluationStatus;

    // 权限映射
    authority: AuthorityMap;
  };
}
```

## 项目状态枚举

### ProjectState (项目状态)

```typescript
enum ProjectState {
  IN_PROGRESS = 1,    // 进行中
  COMPLETED = 2,      // 已完成
  CHANGING = 3,       // 变更中
  PAUSED = 4,         // 已暂停
  ARCHIVED = 5        // 已归档
}

interface StateColor {
  explain: string;
  code: number;
  color: {
    describe: string;
    primary: string;
    minor: string;
  };
  isDelayed: boolean;
}
```

## 人员数据模型

### Creator (创建者)

```typescript
interface Creator {
  id: number;              // 用户 ID
  nickname: string;        // 用户昵称
  avatar: string;          // 头像 URL
}
```

### Owner (项目负责人)

```typescript
interface Owner {
  id: number;              // 用户 ID（注意：不是 open_id）
  nickname: string;        // 用户昵称
  avatar: string;          // 头像 URL
}
```

**⚠️ 重要说明**:
- 接口返回的 `owner` 对象使用 `id` 字段，而非 `open_id`
- 前端代码中使用 `owner.id` 进行数据绑定和 API 调用

### Follower (关注人)

```typescript
interface Follower {
  open_id: string;         // 飞书 open_id
  nickname: string;
  avatar: string;
}
```

**注意**: 关注人列表使用 `open_id` 字段，与 `owner` 的 `id` 字段不同

### User (用户列表 - 用于下拉选择)

```typescript
interface User {
  id: number;
  open_id: string;
  nickname: string;
  nicknamePinyin: string[];  // 拼音（用于搜索）
  avatar: string;
}
```

## 客户数据模型

### Customer

```typescript
interface Customer {
  id: number;
  name: string;
  model_id: number;
  model: string;
}
```

## 节点数据模型

### Nodes (节点集合)

```typescript
interface Nodes {
  current: CurrentNode;
  list: Node[];
}
```

### CurrentNode (当前选中节点)

```typescript
interface CurrentNode {
  id: number;
  name: string;
}
```

### Node (节点)

```typescript
interface Node {
  // 节点基本信息
  id: number;
  name: string;
  category: NodeCategory;    // 节点类型
  parent_id: number | null;

  // 节点状态
  state: NodeState;

  // 节点排期
  schedule: NodeSchedule;

  // 节点负责人
  owners: NodeOwner[];
  owner: NodeOwner | null;   // 兼容旧代码的主负责人

  // 子节点
  sub_nodes: Node[];

  // 其他
  is_delivery: boolean;      // 是否交付节点
}
```

### NodeCategory (节点类型)

```typescript
enum NodeCategory {
  MILESTONE = 1,    // 里程碑
  MAIN = 2,         // 主节点
  SUB = 3           // 子节点
}
```

### NodeState (节点状态)

```typescript
interface NodeState {
  explain: string;          // 状态说明
  code: NodeStateCode;      // 状态码
  color: StateColor;        // 状态颜色
  isDelayed: boolean;       // 是否延期
}

enum NodeStateCode {
  COMPLETED = 0,      // 已完成
  IN_PROGRESS = 1,    // 进行中
  NOT_STARTED = 4     // 未开始
}
```

### NodeSchedule (节点排期)

```typescript
interface NodeSchedule {
  start: string | null;     // 开始时间
  end: string | null;       // 结束时间
  is_overdue: boolean;      // 是否逾期
}
```

### NodeOwner (节点负责人)

```typescript
interface NodeOwner {
  id: number;               // 负责人记录 ID
  user_id: number;          // 用户 ID
  is_major: boolean;        // 是否主负责人
  standard_time: number;    // 标准工时（小时）
  user?: {
    id: number;
    nickname: string;
    avatar: string;
  };

  // 前端扩展字段
  tempId?: number;
  userId?: number;
  tempUserId?: number;
  working_hours?: number;
  tempWorkingHours?: number;
  focus?: boolean;
}
```

## 权限数据模型

### AuthorityMap (权限映射)

```typescript
type AuthorityMap = {
  [permissionCode: number]: boolean
};
```

### 权限码分类

```typescript
// 项目级权限 (1xxx)
enum ProjectPermission {
  EDIT_NAME = 1001,        // 编辑项目名称
  EDIT_DESCRIPTION = 1002, // 编辑项目描述
  EDIT_MODEL = 1003,       // 编辑机型
  EDIT_PRIORITY = 1004,    // 编辑优先级
  EDIT_DEADLINE = 1005,    // 编辑交付日期
  EDIT_FOLLOWERS = 1006,   // 编辑关注人
  // ... 更多项目级权限
  EDIT_OWNER = 1200,       // 编辑项目负责人
  EDIT_TIMELINE = 2400,    // 编辑时间线
  BATCH_EDIT_NODE_OWNER = 2600,  // 批量编辑节点负责人
}

// 节点级权限 (2xxx)
enum NodePermission {
  EDIT_NODE_OWNER = 2001,      // 编辑节点负责人
  EDIT_NODE_TASKS = 2002,      // 编辑节点任务
  EDIT_NODE_HOUR = 2004,       // 编辑节点工时
  EDIT_NODE_SCORE = 2005,      // 节点评分
  EDIT_NODE_SCHEDULE = 2008,   // 编辑节点排期
}
```

## 评价数据模型

### EvaluationStatus

```typescript
interface EvaluationStatus {
  value: 'NOT_EVALUATED' | 'PARTIALLY_EVALUATED' | 'ALL_EVALUATED';
  label: string;
  color: string;
}
```

## Vuex Store 数据模型

### State

```typescript
interface RootState {
  // 用户信息
  userinfo: {
    id: number;
    open_id: string;
    nickname: string;
    avatar: string;
    is_superuser: boolean;
  };

  // 项目数据
  projectData: {
    nodeList: Node[];      // 节点列表
    taskListGuid: string;  // 任务清单 GUID
  };

  // 权限
  authority: {
    project: AuthorityMap;  // 项目级权限
    node: AuthorityMap;     // 节点级权限
  };

  // 项目状态
  projectState: {
    state: ProjectState;
    is_archive: boolean;
  };

  // 机型名称
  modelName: string;

  // 全局枚举
  conciseEnum: {
    difficulty: EnumItem[];
    workload: EnumItem[];
    business: EnumItem[];
    delivery: EnumItem[];
  };
}

interface EnumItem {
  label: string;
  value: number;
  point: number;
}
```

## 表单数据模型

### BasicInfoForm (基本信息表单)

```typescript
interface BasicInfoForm {
  name: string;
  resetName: string;
  content: string;
  deadline_time: string;
  is_overdue: boolean;

  customer: {
    id: number;
  };

  model: {
    name: string;
    initName: string;
    focus: boolean;
  };

  priority: number;

  owner: {
    value: number;  // 注意：使用 owner.id
  };

  follower: {
    list: User[];
    value: string[];  // open_id 数组
  };

  client: {
    range: SelectOption[];
  };
}
```

### SelectOption (下拉选项)

```typescript
interface SelectOption {
  text: string;
  value: number | string;
}
```

## API 请求/响应模型

### 设置节点负责人请求

```typescript
interface SetNodeOwnerRequest {
  node_owners: string[];  // 格式: ["{node_id}:{user_id}", ...]
}

interface SetNodeOwnerResponse {
  data: NodeOwner[];  // 返回完整的 owners 数组
}
```

### 修改项目负责人请求

```typescript
interface ChangeProjectOwnerRequest {
  project_id: string;
  user_id: number;  // 注意：使用 user_id 而非 open_id
}
```

## 数据转换规则

### Owner 数据转换

```javascript
// 接口返回 → 表单绑定
this.formData.owner.value = owner.id  // ✅ 正确
this.formData.owner.value = owner.open_id  // ❌ 错误

// 表单选择 → API 请求
data: {
  project_id: this.projectId,
  user_id: e.id  // ✅ 正确
}
data: {
  project_id: this.projectId,
  open_id: e.open_id  // ❌ 错误（除非后端支持）
}
```

### Follower 数据转换

```javascript
// 接口返回 → 表单绑定
this.formData.follower.value = followers.map(item => item.open_id)  // ✅ 正确

// 表单选择 → API 请求
data: {
  project_id: this.projectId,
  open_id  // ✅ 正确（关注人使用 open_id）
}
```

## 常见数据问题

### 问题 1: 负责人显示为空

**原因**: 接口返回的 `owner` 对象使用 `id` 字段，但代码尝试访问 `owner.open_id`

**解决方案**:
```javascript
// 错误
this.formData.owner.value = owner.open_id

// 正确
this.formData.owner.value = owner.id
```

### 问题 2: 节点负责人列表显示错误

**原因**: `owners` 数组与 `owner` 对象的数据结构不一致

**解决方案**:
```javascript
// owners 是数组
node.owners = [
  { id: 1, user_id: 100, is_major: true, user: {...} },
  { id: 2, user_id: 101, is_major: false, user: {...} }
]

// owner 是单个对象（兼容旧代码）
node.owner = {
  id: 1,
  userId: 100,
  tempId: 1,
  open_id: 'xxx',  // 可能存在
  working_hours: 8
}
```

## 数据初始化流程

```javascript
// 1. 接口返回数据
const res = await this.$util.request({
  url: 'project/list',
  data: { project_id: this.projectId }
})

// 2. 提取核心数据
const { name, nodes, owner, creator, state, authority } = res.data.data

// 3. 设置 Vuex
this.setProjectState({ state })
this.setOwner(owner)
this.setCreator(creator)
this.setAuthority({ project: authority })

// 4. 处理节点列表
this.processNodeList(nodes.list)

// 5. 设置当前选中节点
this.setCurrentNode(nodes.current)
```
