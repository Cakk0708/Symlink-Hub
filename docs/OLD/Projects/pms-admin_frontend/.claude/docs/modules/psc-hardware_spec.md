# PSC 硬件规格模块专家技能

## 模块定位

PSC 硬件规格（Hardware Spec）模块是 PMS 系统中硬件设备管理的核心模块，负责管理项目中使用的各类硬件规格信息。该模块实现了硬件规格的定义、版本控制、机型分类、以及与项目的关联管理。

## 模块职责边界

### 核心职责
1. **硬件规格管理**：硬件规格的增删改查、启用/禁用状态管理
2. **版本管理**：硬件规格的多版本管理，版本的新增、删除、状态切换
3. **机型分类管理**：硬件分类的树形结构管理，支持层级分类
4. **项目关联**：硬件规格与使用项目的关联管理
5. **同步更新**：硬件规格变更后同步到已使用该规格的项目

### 模块边界
- **上游依赖**：无，硬件规格是基础数据
- **下游关联**：项目模板、项目实例
- **非职责范围**：硬件库存管理（属于WMS模块）、硬件采购管理（属于SMS模块）

## 核心数据模型

### HardwareSpec（硬件规格）
```
{
  id: number                      // 硬件规格ID
  name: string                    // 硬件名称
  category: number                // 机型分类ID（外键关联HardwareCategory）
  creator: string                 // 创建者
  createTime: string              // 创建时间
  state: 'AVAILABLE' | 'UNAVAILABLE'  // 状态
  remark: string                  // 备注
  versions: Version[]             // 版本列表
}
```

### Version（硬件版本）
```
{
  id: number                      // 版本ID
  version: string                 // 版本号
  state: 'AVAILABLE' | 'UNAVAILABLE'  // 版本状态
  remark: string                  // 版本备注
  use: number                     // 使用项目数量
  isCreated: boolean              // 是否为新增（前端临时标识）
  versionFocus: boolean           // 版本号输入框聚焦状态
  statusFocus: boolean            // 状态选择框聚焦状态
  remarkFocus: boolean            // 备注输入框聚焦状态
}
```

### HardwareCategory（机型分类）
```
{
  id: number                      // 分类ID
  name: string                    // 分类名称
  parentId: number | null         // 父分类ID（null表示根分类）
  children: HardwareCategory[]    // 子分类（树形结构）
}
```

### Project（使用项目）
```
{
  id: number                      // 项目ID
  name: string                    // 项目名称
  version_name: string            // 硬件版本名称
  creator: string                 // 创建者
  createTime: string              // 创建时间
  state_expand: {                 // 状态扩展信息
    explain: string               // 状态说明
  }
}
```

## API 规范文档

### 1. 硬件规格列表
```javascript
GET /psc/hardware/spec

Request Query Parameters:
{
  pageNum: number        // 页码
  pageSize: number       // 每页数量
  name?: string          // 硬件名称（模糊搜索）
  category?: number      // 机型分类ID
  state?: string         // 状态筛选
  pageSort?: string      // 排序（格式：字段:ASC/DESC）
}

Response:
{
  data: HardwareSpec[]   // 硬件规格列表
  total: number          // 总数
}
```

### 2. 硬件规格详情
```javascript
GET /psc/hardware/spec/{id}

Response:
{
  data: {
    id: number
    name: string
    category: number
    creator: string
    createTime: string
    state: string
    remark: string
    versions: Version[]
  }
}
```

### 3. 新增硬件规格
```javascript
POST /psc/hardware/spec

Request Body:
{
  name: string                    // 硬件名称（必填）
  category: number                // 机型分类ID（必填）
  remark?: string                 // 备注
  version_list: Array<{           // 版本列表（必填）
    version: string               // 版本号（必填）
    state: 'AVAILABLE'            // 状态（默认AVAILABLE）
    remark?: string               // 版本备注
  }>
}

Response:
{
  data: {
    insertId: number              // 新增的硬件规格ID
  }
}
```

### 4. 更新硬件规格
```javascript
POST /psc/hardware/spec  // v2版本使用POST更新

Request Body:
{
  id: number                     // 硬件规格ID（必填）
  name: string                   // 硬件名称
  category: number               // 机型分类ID
  state: string                  // 状态
  remark: string                 // 备注
  version_list: Array<{
    id?: number                  // 已有版本ID（更新时提供）
    version: string              // 版本号
    state: string                // 状态
    remark: string               // 备注
  }>
}

Response:
{
  data: {
    id: number                   // 返回当前版本ID
  }
}
```

### 5. 删除硬件规格
```javascript
DELETE /psc/hardware/spec/{id}

Parameters:
- id: string                    // 多个ID用逗号分隔

Response:
{
  msg: string                   // 'success' 表示成功
}
```

### 6. 启用/禁用硬件规格
```javascript
PATCH /psc/hardware/spec/{id}

Request Body:
{
  state: 'AVAILABLE' | 'UNAVAILABLE'  // 目标状态
}

Response:
{
  msg: string                   // 'success' 表示成功
}
```

### 7. 机型分类列表
```javascript
GET /psc/hardware/category

Response:
{
  data: HardwareCategory[]      // 树形结构的分类列表
}
```

### 8. 新增机型分类
```javascript
POST /psc/hardware/category

Request Body:
{
  name: string                  // 分类名称
}

Response:
{
  msg: string
}
```

### 9. 删除机型分类
```javascript
DELETE /psc/hardware/category/{id}

Response:
{
  msg: string
}
```

### 10. 使用项目列表
```javascript
GET /psc/hardware/project

Request Query Parameters:
{
  versionId: string             // 版本ID（多个ID用逗号分隔）
  all: boolean                  // 是否获取全部项目
  pageNum: number
  pageSize: number
}

Response:
{
  data: Project[]
  total: number
}
```

### 11. 同步项目
```javascript
POST /psc/hardware/project

Request Body:
{
  versionId: string             // 目标版本ID
  projectId: string             // 项目ID（多个ID用逗号分隔）
}

Response:
{
  msg: string
}
```

## 权限验证流程

### 权限类型
1. **查看权限**：`PMS.view_hardware_spec` - 所有用户默认可查看
2. **编辑权限**：`PMS.change_hardware_spec` - 控制编辑、新增、保存功能
3. **删除权限**：`PMS.delete_hardware_spec` - 控制删除功能
4. **启用禁用权限**：`PMS.disable_hardware_spec` - 控制启用/禁用功能

### 权限控制实现
```javascript
const permitStatus = ref({
  disabled: false,              // true表示仅查看权限，所有编辑功能禁用
  deletePermission: true,       // false表示无删除权限
  onOffPermission: true         // false表示无启用禁用权限
})
```

### 权限验证逻辑
```javascript
const initPermitStatus = () => {
  const totalPermission = validatePerm('PMS.change_hardware_spec', false);
  const deletePermission = validatePerm('PMS.delete_hardware_spec', false);
  const onOffPermission = validatePerm('PMS.disable_hardware_spec', false);

  if (!totalPermission) {
    permitStatus.value = {
      disabled: true,
      deletePermission: !deletePermission,
      onOffPermission: !onOffPermission
    };
  }
}
```

## 认证与授权区别说明

### 认证（Authentication）
- 确认用户身份（通过Token）
- 由 `utils/request.js` 统一处理
- 所有API调用都需要认证

### 授权（Authorization）
- 确认用户权限（通过权限校验）
- 在组件层面通过 `validatePerm()` 函数实现
- 不同操作对应不同权限点

## 与其他模块关系

### 1. 项目模板（ProjectTemplate）
- 项目模板可以引用硬件规格
- 硬件规格变更时需要考虑对已创建项目的影响

### 2. 项目实例（Project）
- 项目实例使用具体的硬件版本
- 通过版本ID关联项目

### 3. 交付物定义（DeliverableDefinition）
- 某些交付物可能与特定硬件规格相关

## 常见业务场景

### 场景1：新增硬件规格
1. 点击"新增"按钮跳转到新增页面
2. 填写硬件名称、选择机型分类（必填）
3. 默认创建一个可用版本
4. 保存后自动跳转到编辑页面

### 场景2：编辑硬件规格
1. 双击行或点击硬件名称跳转到编辑页面
2. 可修改基础信息（备注）
3. 机型分类不可修改
4. 可新增/删除/编辑版本
5. 版本号点击可编辑，状态点击可切换
6. 保存后返回更新后的版本ID

### 场景3：删除版本
1. 选择要删除的版本（多选）
2. 点击"删除"按钮
3. 校验：已使用的版本（use > 0）不能删除
4. 删除成功后清空选择

### 场景4：同步硬件到项目
1. 选择单个版本（仅支持单选）
2. 点击"同步"按钮
3. 校验：版本列表有未保存修改时提示先保存
4. 弹出对话框显示使用该版本的项目列表
5. 选择要同步的目标项目
6. 确认后执行同步操作

### 场景5：启用/禁用硬件规格
1. 选择硬件规格（单选/多选）
2. 点击"启用"下拉菜单选择启用或禁用
3. 确认后批量更新状态

## 技术实现建议

### 1. 版本管理策略
- 使用 `isCreated` 标识区分新增和已有的版本
- 新增版本提交时只包含 `version`、`state`、`remark`
- 已有版本更新需要提供 `id`

### 2. 单元格编辑交互
- 点击单元格时将对应字段设置为编辑状态
- 失焦时保存修改并退出编辑状态
- 使用 `nextTick` 确保焦点正确设置

### 3. 树形分类处理
- 使用虚拟根节点（id=0, name="全部"）
- 点击虚拟根节点时清空分类筛选
- 点击其他节点时按分类ID筛选

### 4. 分页处理
- 使用 `LYTable` 组件的内置分页
- 配合 `Pagination` 组件显示使用项目列表
- 版本选择变更时重置页码

### 5. 状态映射
```javascript
const options = reactive({
  status: [
    { label: '可用', value: 'AVAILABLE' },
    { label: '禁用', value: 'UNAVAILABLE' }
  ],
  categories: []  // 从API获取并转换为 {label, value} 格式
})
```

## 扩展设计策略

### 1. 版本历史追溯
- 添加版本创建时间、创建者字段
- 实现版本变更历史记录

### 2. 硬件规格导入导出
- 支持Excel批量导入硬件规格
- 支持导出硬件规格清单

### 3. 规格校验规则
- 添加版本号格式校验
- 添加规格必填字段校验

## 演进方向（Future Evolution）

### 短期目标
1. 完善权限控制细粒度管理
2. 添加硬件规格变更审批流程
3. 优化同步操作的用户体验

### 中期目标
1. 实现硬件规格模板功能
2. 添加规格间依赖关系管理
3. 支持规格组合（多个硬件组合成套件）

### 长期目标
1. 建立硬件规格知识图谱
2. AI辅助硬件规格推荐
3. 与供应链系统集成实现规格标准化

## 模块特有名词解释

| 名词 | 说明 |
|------|------|
| 硬件规格 | 硬件设备的技术规格定义，包含硬件的基础信息和版本 |
| 版本 | 硬件规格的具体版本，每个规格可以有多个版本 |
| 机型分类 | 硬件的分类体系，采用树形结构管理 |
| 同步 | 将硬件规格的变更更新到已使用该规格的项目 |
| 使用项目 | 引用了该硬件规格的项目列表 |

## 前端文件结构

```
src/views/psc/hardware_spec/
├── index.vue                      # 硬件规格列表页
├── add.vue                        # 新增页
├── edit.vue                       # 编辑页
└── components/
    ├── machineRender.vue          # 硬件规格渲染组件（表单+版本表格+使用项目）
    └── dialogPop.vue              # 同步确认弹窗

src/api/pm/hardwarespec.js         # API接口定义
```

## 关键代码位置

- **列表页**: `src/views/psc/hardware_spec/index.vue:1`
- **新增页**: `src/views/psc/hardware_spec/add.vue:1`
- **编辑页**: `src/views/psc/hardware_spec/edit.vue:1`
- **渲染组件**: `src/views/psc/hardware_spec/components/machineRender.vue:1`
- **同步弹窗**: `src/views/psc/hardware_spec/components/dialogPop.vue:1`
- **API定义**: `src/api/pm/hardwarespec.js:1`
