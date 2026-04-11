
# SM 版本管理模块 (versionControl)

## 模块概述

**模块路径**: `SM/version_control`
**功能说明**: 为 PMS 项目做版本发布记录，支持多个版本但只有一个最新版本，支持增删改查、设置当前版本等操作。

---

## API 接口

### 基础路径
- **应用**: SM (系统管理)
- **模块路径**: `/sm/version`

### 接口列表

#### 1. 获取版本列表
- **方法**: `GET /sm/version`
- **参数**: `pageNum`, `pageSize`, `version`, `isCurrent`
- **返回**: `{ items: [...], total: number }`
- **字段**: `id`, `code`, `version`, `isCurrent`, `remark`, `creatorName`, `createTime`, `updateTime`, `itemCount`, `content`

#### 2. 创建版本
- **方法**: `POST /sm/version`
- **参数**: `{ version, isCurrent, remark, itemData: [{ content, sort }] }`
- **返回**: `{ insertedId: number }`
- **说明**: `sort` 从 1 开始

#### 3. 批量删除版本
- **方法**: `DELETE /sm/version`
- **参数**: `{ ids: number[] }`
- **返回**: `{ msg: "success" }`

#### 4. 批量修改版本
- **方法**: `PATCH /sm/version`
- **参数**: `{ ids: number[], isCurrent: boolean }`
- **说明**: 设置当前版本，只能有一个

#### 5. 获取版本详情
- **方法**: `GET /sm/version/{id}`
- **返回**: `{ id, document: {...}, items: [...], others: {...} }`

#### 6. 更新版本
- **方法**: `PUT /sm/version/{id}`
- **参数**: `{ version, isCurrent, remark, itemData: [{ id?, content, sort }] }`
- **说明**: `sort` 从 1 开始；包含 `id` 表示更新，不包含表示新增；未包含的现有项会被删除

#### 7. 获取当前版本
- **方法**: `GET /sm/version/current`

---

## 数据模型

### VersionControl (版本主模型)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| code | string | 版本编码（自动生成，新增/编辑时不显示，查看时显示） |
| version | string | 版本号（必填） |
| is_current | boolean | 是否为当前版本 |
| remark | string | 备注 |
| creator | string | 创建人 |
| create_time | datetime | 创建时间 |
| update_by | string | 最后修改人 |
| update_time | datetime | 最后修改时间 |

### VersionControlItem (版本内容项模型)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| content | string | 更新内容 |
| sort | int | 排序（从 1 开始） |

---

## 文件结构

```
src/
├── api/sm/
│   └── versionControl.js          # API 接口
├── views/sm/versionControl/
│   ├── index.vue                  # 列表页面
│   ├── add.vue                    # 新增页面
│   ├── edit.vue                   # 编辑页面
│   └── components/
│       └── versionRender.vue      # 版本渲染组件
└── router/modules/
    └── sm.js                      # SM 路由配置
```

---

## UI 设计方案

### 列表页面 (index.vue)

**搜索条件**:
- 版本编号 (code)
- 版本号 (version)
- 当前版本 (isCurrent: 是/否)

**表格列**:
1. 选择框 (selection)
2. 版本编号 (code) - 可点击跳转
3. 版本号 (version)
4. 当前版本 (是/否)
5. 更新内容 (content) - 省略显示 + Tooltip 悬浮
6. 创建人 (creatorName)
7. 创建时间 (createTime)
8. 备注 (remark)

**操作按钮**:
- 新增
- 删除 (批量)
- 业务操作下拉: 设为当前版本

**Tooltip 样式**:
- 最大宽度: 400px
- 最大高度: 300px，超出滚动
- 自动换行

### 详情/编辑页面 (edit.vue / add.vue)

**布局**: 使用 versionRender 组件

**版本基础信息**:
- 版本编号 (code) - 仅查看模式显示，禁用
- 版本号 (version) - 必填
- 设为当前版本 (isCurrent) - Switch 开关，仅编辑模式显示
- 备注 (remark) - Textarea

**更新内容**:
- 操作按钮: 新增、删除 (批量)
- 表格列: 选择框、序号、更新内容 (Textarea)
- 删除逻辑: 仅删除勾选的行

**其他信息** (LYOther 组件):
- 创建人
- 创建时间
- 最后更新人
- 最后更新时间

---

## 交互方案

### 更新内容列表交互

**参考模块**: PM/evaluationconfig

**方案**:
1. 表格上方操作区: `table-operate` + `table-operate-item`
2. 按钮文字: "新增"、"删除" (不是"新增更新内容")
3. 删除按钮: 支持批量删除，选中项时才可用
4. 表格: 带多选列 (selection)
5. 每行: 无单独删除按钮

**代码示例**:
```vue
<div class="table-operate">
  <el-button class="table-operate-item" text type="primary" @click="addRow">新增</el-button>
  <el-button class="table-operate-item" text type="primary" @click="delRow" :disabled="multiple">删除</el-button>
</div>
<el-table @selection-change="handleSelectionChange">
  <el-table-column type="selection" width="50" />
</el-table>
```

**新增行**: 生成临时 id
```javascript
props.updateContentList.push({
  id: Math.floor(Math.random() * 10000) + "" + new Date().getTime(),
  content: ''
});
```

**删除逻辑**: 从后往前删除
```javascript
for (let i = props.updateContentList.length - 1; i >= 0; i--) {
  if (idsToDelete.includes(props.updateContentList[i].id)) {
    props.updateContentList.splice(i, 1);
  }
}
```

---

## 代码规范

### API 请求格式

**新增** (POST):
```javascript
{
  version: "1.0.0",
  isCurrent: false,
  remark: "备注",
  itemData: [
    { content: "更新内容", sort: 1 }
  ]
}
```

**更新** (PUT):
```javascript
{
  version: "1.0.1",
  isCurrent: false,
  remark: "备注",
  itemData: [
    { id: 1, content: "更新", sort: 1 },    // 更新现有项
    { content: "新增", sort: 2 }            // 新增项
  ]
}
```

**批量删除** (DELETE):
```javascript
{ ids: [1, 2, 3] }
```

**设置当前版本** (PATCH):
```javascript
{ ids: [1], isCurrent: true }
```

### 数据映射

**列表数据**:
```javascript
versionList.value = list.map((item) => ({
  id: item.id,
  code: item.code,
  version: item.version,
  isCurrent: item.isCurrent ? "是" : "否",
  updateContent: item.content || '',
  creatorName: item.creatorName,
  createTime: item.createTime,
  remark: item.remark,
}));
```

**详情数据 (edit.vue)**:
```javascript
// 基本信息
formData.value = { id: route.params.id, ...res.data.document };

// others 字段映射
formData.value.others = {
  creator: { username: res.data.others.creator },
  createTime: res.data.others.createTime,
  updatedBy: { username: res.data.others.updatedBy },
  updateTime: res.data.others.updateTime
};

// 更新内容列表
updateContentList.value = res.data.items.map(item => ({
  id: item.id,
  content: item.content,
  sort: item.sort
}));
```

### 新增成功后跳转

**关键**: 使用 `router.replace` 而不是 `router.push`，避免退出时返回到新增页

```javascript
await addVersion(submitData).then(res => {
  modal.msgSuccess("新增成功");
  const newId = res.data?.insertedId;
  if (newId) {
    useTagsViewStore().delView(route);
    router.replace({ path: `/sm/versionControl/edit/${newId}/edit` });
  }
});
```

---

## 注意事项

1. **sort 从 1 开始** (不是从 0)
2. **版本编号**: 新增/编辑时不显示，查看时显示只读
3. **删除**: 组件内删除使用 `delVersion([id])` (传递数组)
4. **others 字段**: 需要映射为 LYOther 组件需要的格式 `{ creator: { username }, ... }`
5. **Tooltip**: 长内容需要限制宽度高度，超出滚动
6. **更新内容列表**: 新增时生成临时 id，删除时从后往前遍历
