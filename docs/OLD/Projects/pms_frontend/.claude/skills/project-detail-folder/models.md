# PMS 文件管理模块 - 数据模型定义

## 接口数据模型

### 文件夹列表响应 (FolderListResponse)

```typescript
interface FolderListResponse {
  msg: string;
  data: {
    items: FolderItem[];
    count: number;
  };
}

interface FolderItem {
  id: number;
  name: string;
  deliverables: Deliverable[];
}
```

### 交付物 (Deliverable)

```typescript
interface Deliverable {
  id: number;
  name: string;
  version: string | null;
  fileCategory: FileCategory;
  state: DeliverableState;
  createdAt: string;           // ISO 8601 格式
  createdBy: Creator;
}
```

### 文件类别枚举 (FileCategory)

```typescript
enum FileCategory {
  DOCUMENT = 'document',       // 文档文件
  IMAGE = 'image',             // 图片文件
  VIDEO = 'video',             // 视频文件
  URL = 'url'                  // 链接类型
}
```

### 交付物状态枚举 (DeliverableState)

```typescript
enum DeliverableState {
  INITIAL = 'INITIAL',                         // 初始状态
  INITIAL_FROZEN = 'INITIAL_FROZEN',           // 初始冻结
  FROZEN = 'FROZEN'                            // 已冻结
}
```

### 创建者 (Creator)

```typescript
interface Creator {
  id: number;
  nickname: string;
  avatar: string;              // 头像 URL
}
```

## 组件内部数据模型

### 树形节点 (FolderNode)

```typescript
interface FolderNode {
  // 基本属性
  id: number;
  name: string;
  category: number;            // 1 = 文件夹层级
  parent_id: number;

  // 展开状态
  checked: boolean;            // 是否展开
  isCreate: boolean;
  isFousc: boolean;

  // 子节点数据
  file: DeliverableItem[];     // 交付物列表
  sub_nodes: any[];            // 子节点（空）

  // 路径
  path: string;
}
```

### 交付物项 (DeliverableItem)

```typescript
interface DeliverableItem {
  // 基本属性
  id: number;
  name: string;
  version: string | null;
  parent_id: number;

  // 文件类别
  file_category: string;       // '' | 'url' (用于判断)
  fileCategory: string;        // 原始类别值

  // 状态
  state: number;               // 1 = 正常, 2 = 冻结

  // 时间
  create_time: string;         // 格式化后的时间
  createdAt: string;           // 原始时间

  // 创建者
  creator: Creator;
  createdBy: Creator;

  // 控制标志
  checked: boolean;
  isCreate: boolean;
  isPermission: boolean;

  // 子节点
  sub_nodes: any[];
}
```

## 数据转换映射

### 接口 → 组件 转换表

| 接口字段 | 组件字段 | 类型转换 | 默认值 |
|---------|---------|----------|--------|
| `items[]` | `folderData[]` | 数组 | - |
| `id` | `id` | number | - |
| `name` | `name` | string | - |
| `deliverables[]` | `file[]` | 数组 | `[]` |
| `deliverables.id` | `file.id` | number | - |
| `deliverables.name` | `file.name` | string | - |
| `deliverables.version` | `file.version` | string\|null | `null` |
| `deliverables.fileCategory` | `file.fileCategory` | string | - |
| `deliverables.fileCategory` | `file.file_category` | ternary | `''` |
| `deliverables.state` | `file.state` | transform | `1` |
| `deliverables.createdAt` | `file.create_time` | string | - |
| `deliverables.createdAt` | `file.createdAt` | string | - |
| `deliverables.createdBy` | `file.creator` | object | - |
| `deliverables.createdBy` | `file.createdBy` | object | - |
| - | `file.category` | number | `1` |
| - | `file.checked` | boolean | `false` |
| - | `file.isCreate` | boolean | `true` |
| - | `file.isPermission` | boolean | `true` |
| - | `file.sub_nodes` | array | `[]` |
| - | `category` | number | `1` |
| - | `checked` | boolean | `false` |
| - | `isCreate` | boolean | `true` |
| - | `isFousc` | boolean | `false` |
| - | `sub_nodes` | array | `[]` |
| - | `path` | string | `name` |
| - | `parent_id` | number | `0` |

### 状态转换函数

```typescript
function transformState(state: DeliverableState): number {
  // 字符串状态 → 数字状态
  if (state && state.includes('FROZEN')) {
    return 2; // 冻结
  }
  return 1; // 正常
}

// 映射关系
const STATE_MAP: Record<DeliverableState, number> = {
  'INITIAL': 1,
  'INITIAL_FROZEN': 2,
  'FROZEN': 2
};
```

### 文件类别转换

```typescript
function transformFileCategory(category: FileCategory): string {
  if (category === FileCategory.URL) {
    return 'url';
  }
  return '';
}
```

## 表头配置模型

### 表头列 (HeaderColumn)

```typescript
interface HeaderColumn {
  title: string;               // 列标题
  width: number;               // 列宽（px）
}

// 默认配置
const HEAD_DATA: HeaderColumn[] = [
  { title: '名称', width: 720 },
  { title: '创建者', width: 192 },
  { title: '创建时间', width: 194 },
  { title: '', width: 44 }
];
```

## 样式数据模型

### 头像样式 (AvatarStyle)

```scss
// 变量定义
$avatar-size: 20px;
$avatar-border-radius: 50%;
$avatar-margin-right: 4px;

// 组件类
.avatar-with-name {
  display: flex;
  align-items: center;

  .avatar {
    width: $avatar-size;
    height: $avatar-size;
    overflow: hidden;
    border-radius: $avatar-border-radius;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: $avatar-margin-right;

    image {
      width: 100%;
    }
  }

  .nickname {
    font-size: 12px;
    color: #505050;
  }
}
```

## 验证规则

### 文件名验证
```typescript
function validateFileName(name: string): boolean {
  // 文件名不能为空
  if (!name || name.trim().length === 0) {
    return false;
  }

  // 文件名长度限制
  if (name.length > 255) {
    return false;
  }

  // 禁止的字符
  const forbiddenChars = /[<>:"|?*\\]/;
  if (forbiddenChars.test(name)) {
    return false;
  }

  return true;
}
```

### URL 验证
```typescript
function validateURL(url: string): boolean {
  const pattern = /^(http(s)?:\/\/)(www\.)?([a-zA-Z0-9.-]+)\.([a-z]{2,})(\/[^\s]*)?$/;
  return pattern.test(url);
}
```

## 数据初始化流程

```typescript
// 1. 调用接口
const response = await this.$util.request({
  url: `pm/project/${this.projectId}/folder`,
  method: 'GET'
});

// 2. 数据转换
this.folderData = this.transformToTreeStructure(response.data.data.items || []);

// 3. 递归处理
this.recursion(this.folderData);

// 4. 展开文件夹
this.openCatalogue(this.lookUpList);
```

## 数据更新流程

### 添加文件
```typescript
uni.$on('addAttachFiles', (data) => {
  this.addDataRecursion(
    this.folderData,
    data.attachId,
    data.fileName,
    data.fileId,
    data.fileIsUrl
  );
});
```

### 删除文件
```typescript
uni.$on('delAttachFiles', (data) => {
  this.flattenTree(
    this.folderData,
    data.parent_id,
    data.id
  );
});
```

## 常见数据问题

### 问题 1: 创建者信息缺失

**原因**: 接口返回的 `createdBy` 可能为 null

**解决方案**:
```typescript
// 转换时添加默认值
creator: deliverable.createdBy || {
  id: 0,
  nickname: '未知用户',
  avatar: '/static/default-avatar.png'
}
```

### 问题 2: 头像加载失败

**原因**: 头像 URL 无效或网络问题

**解决方案**:
```vue
<image
  :src="item.creator.avatar"
  mode="widthFix"
  @error="handleAvatarError"
/>

<script>
methods: {
  handleAvatarError(e) {
    e.target.src = '/static/default-avatar.png';
  }
}
</script>
```

### 问题 3: 状态显示错误

**原因**: 状态转换逻辑遗漏

**解决方案**:
```typescript
// 使用映射表代替字符串判断
const STATE_MAP: Record<string, number> = {
  'INITIAL': 1,
  'INITIAL_FROZEN': 2,
  'FROZEN': 2,
  // 预留扩展
  'DELETED': 0
};

function transformState(state: string): number {
  return STATE_MAP[state] ?? 1; // 默认为正常
}
```
