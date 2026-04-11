---
name: project-detail-folder
description: PMS 项目详情页文件管理模块专家，负责文件管理标签页的文件夹结构、交付物展示、创建者头像样式、接口数据转换以及树形组件渲染。当用户提到"文件管理"、"delivery-flie"、"文件夹"、"deliverables"、"交付物"、"树形文件"、"文件上传"、"文件冻结"或相关术语时激活此技能。
---

# PMS 项目详情页 - 文件管理模块架构

## 模块定位

文件管理模块是项目详情页的一个核心标签页组件，负责展示和管理项目相关的文件夹结构及交付物文件。

### 路由与文件位置
- **父组件**: `pagesProject/index/index.vue` (项目详情页)
- **组件路径**: `pagesProject/components/delivery-flie.vue`
- **标签页名称**: "文件管理"

## 模块职责边界

### 核心职责
| 职责 | 说明 | 对应组件/方法 |
|------|------|----------------|
| 文件夹结构展示 | 树形展示项目文件夹 | `tree-node.vue` |
| 交付物列表管理 | 文件列表展示与操作 | `tree-child.vue` |
| 创建者信息展示 | 头像+昵称展示 | `.avatar-with-name` |
| 数据结构转换 | 平铺结构→树形结构 | `transformToTreeStructure()` |
| 文件状态管理 | 冻结/解冻状态 | `toggleFreeze()` |

### 边界界定
- **不负责**: 节点交付物上传（由 `node-deliverable` 模块负责）
- **不负责**: 文件实际存储（由后端 S3/OSS 服务处理）
- **不负责**: 文件权限验证（使用项目级权限）

## 核心数据模型

### 接口响应结构

#### 文件夹列表接口
```javascript
GET /pm/project/{ID}/folder

Response: {
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 3,
        "name": "DELIV0002",
        "deliverables": [
          {
            "id": 3,
            "name": "1.pdf",
            "version": null,
            "fileCategory": "document",
            "state": "INITIAL_FROZEN",
            "createdAt": "2026-03-10 18:35:00",
            "createdBy": {
              "id": 1,
              "nickname": "范凯强",
              "avatar": "https://s3-imfile.feishucdn.com/..."
            }
          }
        ]
      }
    ],
    "count": 1
  }
}
```

### 组件内部数据结构

#### 树形节点模型
```typescript
interface FolderNode {
  id: number;
  name: string;
  category: number;           // 层级: 1=文件夹
  checked: boolean;           // 展开状态
  isCreate: boolean;
  isFousc: boolean;
  file: DeliverableItem[];    // 交付物列表
  sub_nodes: any[];           // 子节点（空数组）
  path: string;
  parent_id: number;
}

interface DeliverableItem {
  id: number;
  name: string;
  version: string | null;
  file_category: string;      // '' | 'url'
  fileCategory: string;       // 原始类别
  state: number;              // 1=正常, 2=冻结
  create_time: string;        // 创建时间
  creator: Creator;           // 创建者对象
  createdAt: string;
  createdBy: Creator;
  checked: boolean;
  isCreate: boolean;
  isPermission: boolean;
  sub_nodes: any[];
  parent_id: number;
}

interface Creator {
  id: number;
  nickname: string;
  avatar: string;
}
```

### 文件状态枚举

#### 文件类别 (fileCategory)
| 值 | 说明 |
|----|------|
| `document` | 文档文件 |
| `image` | 图片文件 |
| `video` | 视频文件 |
| `url` | 链接类型 |

#### 文件状态 (state)
| 状态码 | 说明 | 原接口状态值 |
|--------|------|--------------|
| 1 | 正常 | `INITIAL` |
| 2 | 冻结 | `INITIAL_FROZEN`, `FROZEN` |

## 数据转换流程

### 接口数据 → 组件数据

```javascript
// delivery-flie.vue
transformToTreeStructure(items) {
  return items.map(folder => ({
    id: folder.id,
    name: folder.name,
    category: 1,
    checked: false,
    isCreate: true,
    isFousc: false,
    // deliverables → file
    file: (folder.deliverables || []).map(deliverable => ({
      id: deliverable.id,
      name: deliverable.name,
      version: deliverable.version,
      file_category: deliverable.fileCategory === 'url' ? 'url' : '',
      fileCategory: deliverable.fileCategory,
      state: this.transformState(deliverable.state),
      create_time: deliverable.createdAt,
      creator: deliverable.createdBy,
      createdAt: deliverable.createdAt,
      createdBy: deliverable.createdBy,
      checked: false,
      isCreate: true,
      isPermission: true,
      sub_nodes: [],
      parent_id: folder.id
    })),
    sub_nodes: [],
    path: folder.name,
    parent_id: 0
  }))
}

// 状态转换: 字符串 → 数字
transformState(state) {
  if (state && state.includes('FROZEN')) {
    return 2 // 冻结
  }
  return 1 // 正常
}
```

### 字段映射对照表

| 新接口字段 | 组件字段 | 转换说明 |
|-----------|---------|----------|
| `items[]` | `folderData[]` | 文件夹数组 |
| `deliverables[]` | `file[]` | 交付物数组 |
| `createdAt` | `create_time` | 创建时间 |
| `createdBy` | `creator` | 创建者对象 |
| `fileCategory` | `file_category` | URL 类型判断 |
| `state` (字符串) | `state` (数字) | 状态码转换 |
| - | `category` | 默认为 1 |
| - | `checked` | 默认为 false |
| - | `isCreate` | 默认为 true |

## UI 组件结构

### 组件层级

```
delivery-flie.vue          # 主组件
├── treeNode.vue            # 树形容器
│   ├── tree-head          # 表头
│   └── tree-child.vue     # 树节点（递归）
```

### 表头配置

```javascript
headData: [
  { title: '名称', width: 720 },
  { title: '创建者', width: 192 },
  { title: '创建时间', width: 194 },
  { title: '', width: 44 }     // 操作列
]
```

### 创建者头像展示

#### 模板结构
```vue
<!-- tree-child.vue:85-92 -->
<template v-else>
  <view class="avatar-with-name" v-if="item.creator">
    <view class="avatar">
      <image :src="item.creator.avatar" mode="widthFix"></image>
    </view>
    <text class="nickname">{{item.creator.nickname}}</text>
  </view>
</template>
```

#### 样式定义
```scss
.principal {
  .avatar-with-name {
    display: flex;
    align-items: center;
    .avatar {
      width: 20px;
      height: 20px;
      overflow: hidden;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 4px;
      image {
        width: 100%;
      }
    }
    .nickname {
      font-size: 12px;
      color: #505050;
    }
  }
}
```

### 树形展开/收起

```javascript
// 点击展开图标
clickToggle(item) {
  item.checked = !item.checked
}

// 判断显示展开图标
visibility: ((item.sub_nodes && item.sub_nodes.length > 0) ||
            (item.file && item.file.length > 0)) ? 'visible' : 'hidden'
```

## 已废弃功能

### ⚠️ 点击跳转业务 (Deprecated)

```javascript
// tree-child.vue:244-252 (已注释)
// async clickGotoDoc(item){
//   let url = 'pm/deliverable/' + item.id + '/' + item.rule_id ? item.type : 'folder'
//   let res = await this.$util.request({url, method:'POST'})
//   if (res.data.code == 0) {
//     window.open(`https://applink.feishu.cn/client/web_url/open?mode=window&height=700&width=900&url=${res.data.data.url}`)
//   }
// }
```

**原因**: 新接口结构变更，跳转逻辑需要重新实现。

## 与其他模块关系

```
project-detail (项目详情)
    ├── delivery-flie (文件管理)     ← 当前模块
    │   ├── treeNode (树形组件)
    │   └── tree-child (树节点)
    ├── node-details (节点详情)
    │   └── node-deliverable (节点交付物)  # 可能关联
    └── basic-info (基本信息)
```

### 数据流向
```
GET /pm/project/{ID}/folder
    ↓
delivery-flie.vue (transformToTreeStructure)
    ↓
folderData (树形结构)
    ↓
tree-node.vue (渲染)
    ↓
tree-child.vue (递归子节点)
```

### 事件通信
```javascript
// 删除文件事件
uni.$on('delAttachFiles', (data) => {
  this.flattenTree(this.folderData, data.parent_id, data.id)
})

// 添加文件事件
uni.$on('addAttachFiles', (data) => {
  this.addDataRecursion(this.folderData, data.attachId, ...)
})
```

## 常见业务场景

### 场景 1: 加载文件列表
```javascript
// 1. 进入项目详情页
// 2. 切换到"文件管理"标签
// 3. 调用 GET /pm/project/{ID}/folder
// 4. transformToTreeStructure() 转换数据
// 5. recursion() 初始化节点状态
// 6. openCatalogue() 自动展开有文件的文件夹
```

### 场景 2: 展开文件夹
```javascript
// 1. 用户点击展开图标
// 2. clickToggle(item) 切换 checked 状态
// 3. v-if="item.checked" 控制子节点显示
// 4. 递归渲染 tree-child 子组件
```

### 场景 3: 查看创建者信息
```javascript
// 1. 文件列表展示
// 2. 每行显示创建者头像 (20x20) + 昵称
// 3. 头像点击事件（当前未实现）
// 4. 样式参考 zxz-uni-data-select 的负责人展示
```

## 技术实现建议

### 前端 (Vue 2.0)

#### 组件通信
```javascript
// 父传子: props
<treeNode
  :headData='headData'
  :data="folderData"
  type="file"
  :projectId="projectId"
/>

// 递归渲染
<treeChild
  v-for="n in item.file"
  :type="type"
  :setWidth="setWidth"
  :key="n.id"
  :items="item.file"
  :projectId="projectId"
  :item="n"
/>
```

#### 数据初始化
```javascript
async mounted() {
  await this.getFolderData()
  uni.$on('delAttachFiles', (data) => {
    this.flattenTree(this.folderData, data.parent_id, data.id)
  })
  uni.$on('addAttachFiles', (data) => {
    this.addDataRecursion(this.folderData, data.attachId, ...)
  })
}
```

### 后端 (Django)

#### API 设计
```python
# 获取项目文件夹结构
class ProjectFolderViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        """
        获取项目文件夹及交付物列表

        GET /api/pm/project/{project_id}/folder

        Response:
        {
            "msg": "success",
            "data": {
                "items": [
                    {
                        "id": int,
                        "name": str,
                        "deliverables": [
                            {
                                "id": int,
                                "name": str,
                                "version": str | None,
                                "fileCategory": str,  # document|image|video|url
                                "state": str,         # INITIAL|INITIAL_FROZEN|FROZEN
                                "createdAt": str,     # ISO 8601
                                "createdBy": {
                                    "id": int,
                                    "nickname": str,
                                    "avatar": str
                                }
                            }
                        ]
                    }
                ],
                "count": int
            }
        }
        """
        project = get_object_or_404(Project, pk=pk)
        folders = project.folders.all().prefetch_related('deliverables__created_by')

        items = []
        for folder in folders:
            deliverables = []
            for d in folder.deliverables.all():
                deliverables.append({
                    'id': d.id,
                    'name': d.name,
                    'version': d.version,
                    'fileCategory': d.file_category,
                    'state': d.get_state_display(),
                    'createdAt': d.created_at.isoformat(),
                    'createdBy': {
                        'id': d.created_by.id,
                        'nickname': d.created_by.nickname,
                        'avatar': d.created_by.avatar
                    }
                })
            items.append({
                'id': folder.id,
                'name': folder.name,
                'deliverables': deliverables
            })

        return Response({
            'msg': 'success',
            'data': {'items': items, 'count': len(items)}
        })
```

#### 数据模型建议
```python
from django.db import models

class Folder(models.Model):
    """项目文件夹"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

class Deliverable(models.Model):
    """交付物文件"""
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='deliverables')
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50, null=True, blank=True)
    file_category = models.CharField(max_length=20)  # document|image|video|url
    file_url = models.URLField()
    state = models.CharField(max_length=20)  # INITIAL|INITIAL_FROZEN|FROZEN
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 扩展设计策略

### 新增文件类别
1. 更新 `fileCategory` 枚举值
2. 在 `transformToTreeStructure()` 中添加类别判断
3. 添加对应图标展示

### 新增文件状态
1. 后端添加新状态值
2. 更新 `transformState()` 转换逻辑
3. 前端添加状态样式（颜色/图标）

### 实现点击跳转
```javascript
// 需要重新实现的接口
async clickGotoDoc(item) {
  // 1. 调用新接口获取文件预览链接
  // 2. 判断 fileCategory 类型
  // 3. document/video: 飞书文档打开
  // 4. url: 直接跳转
  // 5. image: 预览弹窗
}
```

## 演进方向 (Future Evolution)

### 短期优化
- [ ] 文件上传功能实现
- [ ] 文件拖拽排序
- [ ] 批量下载
- [ ] 文件预览功能

### 中期规划
- [ ] 文件版本管理
- [ ] 文件夹嵌套（多层级）
- [ ] 文件搜索功能
- [ ] 文件权限控制

### 长期愿景
- [ ] 文件在线编辑
- [ ] 文件协作评论
- [ ] 文件变更历史
- [ ] AI 文件分类

## 特有名词索引

| 名词 | 说明 |
|------|------|
| **文件管理** | `delivery-flie.vue` 组件 |
| **文件夹** | `Folder` 数据模型 |
| **交付物** | `Deliverable` 数据模型 |
| **树形结构** | 文件夹的层级展示方式 |
| **创建者头像** | 文件创建者的头像展示 (20x20) |
| **状态冻结** | `state=2` 的文件状态 |
| **数据转换** | 平铺结构 → 树形结构的转换 |

---

**参考文档**:
- `models.md` - 详细数据模型定义
- `evolution.md` - 演进路线图
- `API-reference.md` - API 接口文档
