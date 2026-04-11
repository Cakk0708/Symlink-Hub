# BDM 部门管理模块 (department)

## 模块概述

**模块路径**: `BDM/department`
**功能说明**: 管理企业组织架构中的部门信息，支持部门层级结构、负责人关联、启用/禁用状态控制。部门是员工管理和权限控制的基础组织单元。

**模块定位**:
- **基础数据管理 (BDM)** 核心模块
- 为员工管理提供组织架构支撑
- 为权限控制提供部门级数据隔离
- 支持多层级部门树形结构

---

## 核心职责边界

### 职责范围
- 部门基础信息的 CRUD 操作
- 部门编码的自动生成与管理
- 部门负责人的关联与维护
- 部门上下级关系管理
- 部门启用/禁用状态控制

### 职责边界
- **不包含** 员工的具体管理（由 `bdm-staff` 模块负责）
- **不包含** 权限的具体分配（由权限系统负责，但部门可作为权限维度）
- **不包含** 组织架构的完整可视化（如组织架构图，可能需要独立模块）

---

## API 接口规范

### 基础路径
- **应用**: BDM (业务数据管理)
- **模块路径**: `/bdm/departments`

### 接口列表

#### 1. 获取部门列表
- **方法**: `GET /bdm/departments`
- **查询参数**:
  ```typescript
  {
    pageNum: number;        // 页码，默认 1
    pageSize: number;       // 每页数量，默认 10
    code?: string;          // 部门编码（模糊查询）
    name?: string;          // 部门名称（模糊查询）
    pageSort?: string;      // 排序，格式 "FIELD:ORDER"，如 "ID:DESC"
  }
  ```
- **响应示例**:
  ```json
  {
    "data": {
      "items": [
        {
          "id": 1,
          "primaryId": "dept_001",
          "routeId": "dept_001",
          "code": "DEPT001",
          "name": "研发部",
          "ownerName": "张三",
          "memberQty": 15,
          "disableFlag": false,
          "parentName": "技术中心"
        }
      ],
      "pagination": {
        "total": 1,
        "pageNum": 1,
        "pageSize": 10
      }
    }
  }
  ```

#### 2. 获取部门详情
- **方法**: `GET /bdm/departments/{id}`
- **路径参数**: `id` - 部门 ID
- **响应示例**:
  ```json
  {
    "data": {
      "id": 1,
      "document": {
        "code": "DEPT001",
        "name": "研发部",
        "owner": { "id": 10, "name": "张三" },
        "parent": { "id": 1, "name": "技术中心" }
      },
      "others": {
        "status": "ACTIVE",
        "disableFlag": false,
        "creator": "admin",
        "createTime": "2024-01-01 10:00:00",
        "updatedBy": "admin",
        "updateTime": "2024-03-11 14:30:00"
      }
    }
  }
  ```

#### 3. 新增部门
- **方法**: `POST /bdm/departments`
- **请求参数**:
  ```typescript
  {
    name: string;           // 部门名称（必填）
    ownerId?: number;       // 部门负责人 ID（可选）
    parentId?: number;      // 上级部门 ID（可选）
  }
  ```
- **响应示例**:
  ```json
  {
    "data": {
      "insertedId": 123
    }
  }
  ```
- **说明**: 部门编码 `code` 由后端自动生成，无需前端传递

#### 4. 更新部门
- **方法**: `PUT /bdm/departments/{id}`
- **路径参数**: `id` - 部门 ID
- **请求参数**:
  ```typescript
  {
    code?: string;          // 部门编码（通常不修改）
    name?: string;          // 部门名称
    ownerId?: number;       // 部门负责人 ID
    parentId?: number;      // 上级部门 ID
    disableFlag?: boolean;  // 禁用状态
  }
  ```
- **说明**: 只传递需要修改的字段

#### 5. 删除部门
- **方法**: `DELETE /bdm/departments/{id}`
- **路径参数**: `id` - 部门 ID（支持批量，多个 ID 用逗号分隔）
- **说明**: 批量删除示例 `DELETE /bdm/departments/1,2,3`

---

## 数据模型

### Department (部门主模型)

| 字段 | 类型 | 说明 | 限制 |
|------|------|------|------|
| id | number | 主键 ID | 自增 |
| code | string | 部门编码 | 自动生成，唯一 |
| name | string | 部门名称 | 必填，唯一（同级） |
| ownerId | number | 部门负责人 ID | 外键关联员工表 |
| ownerName | string | 负责人姓名 | 冗余字段，只读 |
| parentId | number | 上级部门 ID | 外键自关联 |
| parentName | string | 上级部门名称 | 冗余字段，只读 |
| memberQty | number | 部门人数 | 统计字段，只读 |
| disableFlag | boolean | 禁用状态 | 默认 false |
| status | string | 状态枚举 | ACTIVE/INACTIVE |

### 响应数据结构说明

**列表响应** (`items` 数组项):
- `primaryId`: 用于表格 rowKey
- `routeId`: 用于路由跳转
- `memberQty`: 实时统计的部门人数
- `disableFlag`: 禁用状态，布尔值

**详情响应** (嵌套结构):
- `document`: 核心业务数据
- `others`: 系统元数据（创建人、时间等）

---

## 文件结构

```
src/
├── api/bdm/
│   └── dept.js                    # API 接口定义
├── views/bdm/department/
│   ├── index.vue                  # 列表页面
│   ├── add.vue                    # 新增页面容器
│   ├── edit.vue                   # 编辑页面容器
│   └── components/
│       └── deptRender.vue         # 表单渲染组件
└── router/modules/
    └── bdm.js                     # BDM 路由配置
```

---

## UI 设计方案

### 列表页面 (index.vue)

**搜索条件**:
- 部门编码 (code) - 模糊搜索
- 部门名称 (name) - 模糊搜索

**表格列配置**:
1. 选择框 (selection) - 固定左侧
2. 部门编码 (code) - 可点击跳转，固定左侧，高亮显示
3. 部门名称 (name)
4. 部门负责人 (ownerName)
5. 部门人数 (memberQty) - 只读统计
6. 禁用状态 (disableFlag) - 字典映射
7. 上级部门 (parentName)

**操作按钮**:
- 新增 - 跳转到新增页面
- 删除 - 批量删除，选中时启用
- 搜索/重置 - 查询条件操作

**交互特性**:
- 双击行跳转到编辑页面
- 单击编码列跳转到编辑页面
- 使用 `createFirstClickExecutor` 防止双击冲突（800ms 去重）

### 详情/编辑页面 (edit.vue / add.vue)

**布局结构**:
```
页面容器 (add.vue/edit.vue)
  └── deptRender 组件
       ├── 基础信息表单区 (LYTitleLabel)
       │   ├── 部门编码 - 禁用，自动生成
       │   └── 部门名称 - 必填输入
       └── 其他信息区 (LYOther，仅编辑显示)
           ├── 创建人
           ├── 创建时间
           ├── 最后更新人
           └── 最后更新时间
```

**表单字段**:
- 部门编码: 只读，显示"保存时自动生成"
- 部门名称: 必填，`{ required: true, message: "部门名称不能为空" }`

**操作按钮**:
- 保存 - 触发表单验证后提交
- 删除 - 仅编辑模式显示
- 退出 - 返回上一页，关闭当前标签

---

## 交互逻辑

### 新增流程

1. 用户点击"新增"按钮
2. 跳转到 `/bdm/department/add`
3. 用户填写部门名称
4. 点击"保存"按钮
5. 前端校验部门名称非空
6. 调用 `POST /bdm/departments`，只传递 `{ name }`
7. 成功后获取 `insertedId`
8. 关闭当前标签，使用 `router.replace` 跳转到编辑页
9. 部门编码由后端自动生成并在编辑页显示

### 编辑流程

1. 从列表页点击编码或双击行
2. 跳转到 `/bdm/department/edit/{id}/edit` 或 `/view`
3. 调用 `GET /bdm/departments/{id}` 获取详情
4. 数据映射到表单:
   ```javascript
   formData.value = {
     id: route.params.id,
     code: res.data.document.code,
     name: res.data.document.name,
     ownerId: res.data.document.owner?.id,
     disabled: res.data.others.disableFlag
   };
   formData.value.others = {
     creator: { username: res.data.others.creator },
     createTime: res.data.others.createTime,
     updatedBy: { username: res.data.others.updatedBy },
     updateTime: res.data.others.updateTime
   };
   ```
5. 用户修改后点击"保存"
6. 只传递修改的字段到 `PUT /bdm/departments/{id}`
7. 成功后显示"更新成功"消息
8. 更新本地 `others.updatedBy` 和 `updateTime`

### 状态切换

- 禁用/启用部门: 调用 `PUT` 更新 `disableFlag` 字段
- 状态变化后同步更新 `formData.others.disableFlag`
- 显示成功消息: "已禁用" 或 "重新启用"

### 删除逻辑

**列表批量删除**:
1. 用户勾选多个部门
2. 点击"删除"按钮
3. 二次确认: "确定要删除选中的信息吗？"
4. 调用 `DELETE /bdm/departments/{ids}` (逗号分隔)
5. 成功后刷新列表，显示"删除成功"

**详情页删除**:
1. 点击"删除"按钮
2. 二次确认: "确定要删除当前数据的信息吗？"
3. 调用 `DELETE /bdm/departments/{id}`
4. 成功后关闭当前标签并返回上一页

---

## 代码规范

### API 调用示例

```javascript
import { getDeptList, addDept, updateDept, delDept } from "@/api/bdm/dept";

// 获取列表
const getList = async () => {
  const res = await getDeptList(queryParams.value);
  deptList.value = res.data.items;
  options.total = res.data.pagination.total;
};

// 新增部门（只传名称）
const clickConfirm = (data) => {
  addDept({ name: data.name }).then(res => {
    modal.msgSuccess("新增成功");
    useTagsViewStore().delView(route);
    router.replace({
      path: `/bdm/department/edit/${res.data.insertedId}/edit`
    });
  });
};

// 更新部门（只传修改字段）
const clickConfirm = async (data) => {
  const billFormData = { name: data.name };
  // code 未变化则不传递
  if (initData.value.code === data.code) {
    delete billFormData.code;
  }
  await updateDept({ ...billFormData, id: route.params.id });
  ElMessage.success('更新成功');
};

// 删除部门
const handleDelete = () => {
  modal.confirm("确定要删除选中的信息吗？")
    .then(() => delDept(ids.join(',')))
    .then(() => {
      getList();
      modal.msgSuccess("删除成功");
    });
};
```

### 表格列配置

```javascript
const tableColumns = reactive([
  { type: "selection", key: "selection", unDraggable: true, show: true, fixed: true },
  {
    label: "部门编码",
    prop: "code",
    sortable: 'custom',
    isHighlight: true,
    isSkip: true,
    key: "code",
    show: true,
    fixed: true
  },
  { label: "部门名称", prop: "name", key: "name", show: true },
  { label: "部门负责人", prop: "ownerName", key: "ownerName", show: true },
  { label: "部门人数", prop: "memberQty", key: "memberQty", show: true },
  {
    label: "禁用状态",
    prop: "disableFlag",
    dict,
    dictType: "disableFlag",
    key: "disableFlag",
    show: true
  },
  { label: "上级部门", prop: "parentName", key: "parentName", show: true },
]);
```

### 路由跳转

```javascript
// 新增
const handleAdd = () => {
  router.push({ path: "department/add" });
};

// 编辑（双击/单击编码）
const handleUpdate = createFirstClickExecutor((row) => {
  const id = row.routeId || row.primaryId;
  if (!id) return;
  router.push({
    path: `department/edit/${id}/edit`
  });
}, 800);

// 新增成功后跳转（使用 replace 避免返回到新增页）
router.replace({
  path: `/bdm/department/edit/${insertedId}/edit`
});
```

---

## 与其他模块关系

### 依赖关系

**上游依赖**:
- 无（部门是基础主数据）

**下游依赖**:
- **bdm-staff (员工管理)**: 员工必须关联到部门
- **sm-user (系统用户)**: 用户可能关联部门进行权限控制
- **权限系统**: 部门级数据权限隔离

### 数据流向

```
部门管理 (bdm-department)
    ↓ 提供组织架构
员工管理 (bdm-staff)
    ↓ 关联部门
用户/权限系统
```

### 关联字段

- `staff.deptId` → `department.id` (员工关联部门)
- `user.departmentId` → `department.id` (用户关联部门，可能)

---

## 常见业务场景

### 场景 1: 新增部门后自动跳转编辑

**需求**: 用户在新增页填写部门名称并保存后，自动跳转到编辑页继续完善信息（如设置负责人）。

**实现**:
```javascript
// add.vue
addDept({ name: data.name }).then(res => {
  modal.msgSuccess("新增成功");
  const newId = res.data.insertedId;
  if (newId) {
    useTagsViewStore().delView(route); // 关闭新增页标签
    router.replace({ // 使用 replace，避免返回到新增页
      path: `/bdm/department/edit/${newId}/edit`
    });
  }
});
```

### 场景 2: 防止双击跳转冲突

**需求**: 列表页单击编码跳转，双击行也跳转，需要避免重复触发。

**实现**:
```javascript
import { createFirstClickExecutor } from '@/utils/index';

const handleUpdate = createFirstClickExecutor((row) => {
  if (!row) return;
  const id = row.routeId || row.primaryId;
  if (!id) return;
  router.push({
    path: `department/edit/${id}/edit`
  });
}, 800); // 800ms 内忽略重复点击
```

### 场景 3: 只传递修改的字段

**需求**: 编辑时只向后端传递实际修改的字段，减少不必要的网络传输和后端处理。

**实现**:
```javascript
const clickConfirm = async (data) => {
  let billFormData = { ...data };

  // code 未变化则删除
  if (initData.value.code === billFormData.code) {
    delete billFormData.code;
  }

  // name 未变化则删除
  if (initData.value.name === billFormData.name) {
    delete billFormData.name;
  }

  await updateDept({ ...billFormData, id: route.params.id });
};
```

---

## 特有名词索引

当未来提到以下名词时，可快速定位到本技能:

| 名词 | 说明 |
|------|------|
| 部门管理 | 本模块的通俗名称 |
| Department | 部门的英文术语 |
| 部门编码 | 部门的唯一标识，自动生成 |
| 部门名称 | 部门的显示名称 |
| 部门负责人 | 关联到部门的员工 |
| 上级部门 | 部门的父节点，支持树形结构 |
| 禁用部门 | disableFlag 字段，控制部门可用性 |
| 部门人数 | memberQty，统计字段 |
| dept | 部门的常见简写 |

---

## 扩展设计策略

### 当前实现
- 基础 CRUD 功能
- 简单的列表展示
- 基础的状态控制（禁用/启用）

### 未来扩展方向

1. **树形结构展示**
   - 支持部门树形组件展示
   - 支持拖拽调整层级关系
   - 支持展开/折叠子部门

2. **部门成员管理**
   - 在部门详情页直接查看和管理成员
   - 支持成员在部门间调动

3. **部门权限配置**
   - 部门级数据权限
   - 部门管理员角色

4. **组织架构图**
   - 可视化展示完整组织架构
   - 支持导出组织架构

5. **部门负责人设置**
   - 当前代码中存在 `ownerId` 字段但未在前端表单显示
   - 未来需要添加部门负责人选择器

---

## 注意事项

1. **编码自动生成**: 部门编码由后端自动生成，新增时不显示，编辑时只读显示
2. **路由跳转**: 新增成功后使用 `router.replace` 而非 `router.push`，避免返回到新增页
3. **去重处理**: 列表页单击编码和双击行都会跳转，使用 `createFirstClickExecutor` 防冲突
4. **部分更新**: 编辑时只传递修改的字段，未修改的字段不传递给后端
5. **状态同步**: 修改 `disableFlag` 后需同步更新 `formData.others.disableFlag`
6. **数据映射**: 详情响应的嵌套结构需要正确映射到组件所需的格式
7. **字典映射**: `disableFlag` 使用字典组件显示，需要在组件中 `inject("loadDict")`

---

## 技术实现建议 (Django 后端)

### 模型设计

```python
class Department(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey('Staff', on=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    parent = models.ForeignKey('self', on=models.SET_NULL, null=True, blank=None, related_name='children')
    disable_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_models.SET_NULL, null=True, related_name='created_departments')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_models.SET_NULL, null=True, related_name='updated_departments')

    class Meta:
        db_table = 'bdm_department'
        verbose_name = '部门'
        verbose_name_plural = '部门'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"
```

### 序列化器

```python
class DepartmentSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    member_qty = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = '__all__'

    def get_member_qty(self, obj):
        return obj.staff_set.filter(disable_flag=False).count()
```

### 视图

```python
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filterset_fields = ['code', 'name', 'disable_flag']
    search_fields = ['code', 'name']

    def perform_create(self, serializer):
        # 自动生成编码
        last_dept = Department.objects.order_by('-id').first()
        new_code = f"DEPT{str(last_dept.id + 1).zfill(3)}" if last_dept else "DEPT001"
        serializer.save(code=new_code, created_by=self.request.user)
```

---

## API 响应示例汇总

### 列表响应

```json
{
  "data": {
    "items": [
      {
        "id": 1,
        "primaryId": "dept_001",
        "routeId": "dept_001",
        "code": "DEPT001",
        "name": "研发部",
        "ownerName": "张三",
        "memberQty": 15,
        "disableFlag": false,
        "parentName": "技术中心"
      }
    ],
    "pagination": {
      "total": 1,
      "pageNum": 1,
      "pageSize": 10
    }
  }
}
```

### 详情响应

```json
{
  "data": {
    "id": 1,
    "document": {
      "code": "DEPT001",
      "name": "研发部",
      "owner": { "id": 10, "name": "张三" },
      "parent": { "id": 1, "name": "技术中心" }
    },
    "others": {
      "status": "ACTIVE",
      "disableFlag": false,
      "creator": "admin",
      "createTime": "2024-01-01 10:00:00",
      "updatedBy": "admin",
      "updateTime": "2024-03-11 14:30:00"
    }
  }
}
```

### 新增响应

```json
{
  "data": {
    "insertedId": 123
  }
}
```

### 更新响应

```json
{
  "msg": "success",
  "data": null
}
```

### 删除响应

```json
{
  "msg": "success"
}
```
