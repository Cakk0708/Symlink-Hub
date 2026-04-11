# PSC 项目角色模块 (ProjectRole)

## 模块定位

项目角色模块是 PSC (Project System Configuration) 项目配置系统的核心基础模块，负责定义项目中各类参与角色的基础信息及其评价属性。该模块为节点定义、评价配置、项目模板等上层模块提供角色数据支撑。

### 核心价值
- 定义项目参与角色的唯一标识（编码）和显示名称
- 控制角色是否参与评价/被评价的二元属性
- 提供角色禁用/反禁用的业务状态管理
- 作为节点定义中"项目角色"字段的选项来源
- 作为评价配置中"角色名称"字段的数据源

---

## 模块职责边界

### 核心职责
1. **角色基础信息管理**
   - 角色编码（code）：自动生成或手动输入，保存时自动生成
   - 角色名称（name）：角色显示名称，必填

2. **评价属性配置**
   - 是否参与评价（isEvaluatable）：布尔值，标识该角色是否有资格评价其他角色
   - 是否被评价（isEvaluated）：布尔值，标识该角色是否接受其他角色评价

3. **业务状态管理**
   - 禁用/反禁用操作（PATCH 请求）
   - 批量禁用/反禁用支持

4. **数据查询服务**
   - 列表查询（分页、筛选）
   - 简单列表查询（供下拉选择使用）
   - 枚举查询（获取字段过滤选项）

### 职责边界
- **不属于本模块**：角色的权限配置（系统用户权限）、角色与项目实例的关联（项目成员管理）
- **关联模块**：
  - `NodeDefinition`：节点定义通过 `projectRoleId` 关联项目角色
  - `EvaluationConfig`：评价配置通过 `projectRoleId` 关联项目角色
  - `ProjectTemplate`：项目模板通过角色配置节点负责人

---

## 核心数据模型

### ProjectRole 数据结构
```javascript
{
  id: Number,                    // 角色ID（主键）
  code: String,                  // 角色编码（保存时自动生成）
  name: String,                  // 角色名称（必填）
  isEvaluatable: Boolean,        // 是否参与评价
  isEvaluated: Boolean,          // 是否被评价
  disableFlag: Boolean,          // 是否禁用
  creator: String,               // 创建人
  createTime: String,            // 创建时间
  hasEvaluationConfig: Boolean   // 是否已有评价配置（衍生属性）
}
```

### 字段说明
| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| code | String | 否 | 自动生成 | 保存时后端自动生成角色编码 |
| name | String | 是 | - | 角色显示名称 |
| isEvaluatable | Boolean | 是 | - | 该角色是否有资格评价其他角色 |
| isEvaluated | Boolean | 是 | - | 该角色是否接受其他角色评价 |
| disableFlag | Boolean | - | false | 禁用标识，禁用后不可在项目模板中使用 |

---

## API 规范文档

### 基础路径
```
/psc/role
```

### 1. 新增项目角色
**请求**
```http
POST /psc/role/add
Content-Type: application/json

{
  "name": "项目经理",
  "isEvaluatable": true,
  "isEvaluated": true
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "insertId": 123
  }
}
```

### 2. 修改项目角色
**请求**
```http
PUT /psc/role/{id}
Content-Type: application/json

{
  "id": 123,
  "name": "项目经理",
  "isEvaluatable": true,
  "isEvaluated": true
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "修改成功",
  "data": null
}
```

### 3. 获取项目角色详情
**请求**
```http
GET /psc/role/{id}
```

**响应示例**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": 123,
    "code": "ROLE_PM_001",
    "name": "项目经理",
    "isEvaluatable": true,
    "isEvaluated": true,
    "disableFlag": false,
    "creator": "admin",
    "createTime": "2024-01-01 12:00:00"
  }
}
```

### 4. 获取项目角色列表（分页）
**请求**
```http
GET /psc/role?pageNum=1&pageSize=10&code=ROLE_PM&name=项目经理
```

**响应示例**
```json
{
  "code": 200,
  "message": "查询成功",
  "total": 50,
  "data": [
    {
      "id": 123,
      "code": "ROLE_PM_001",
      "name": "项目经理",
      "isEvaluatable": true,
      "isEvaluated": true,
      "disableFlag": false,
      "createTime": "2024-01-01 12:00:00"
    }
  ]
}
```

### 5. 获取简单项目角色列表（下拉选项）
**请求**
```http
GET /psc/role/simple?pageNum=1&pageSize=1000
```

**响应示例**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "items": [
      {
        "id": 123,
        "name": "项目经理",
        "code": "ROLE_PM_001",
        "isEvaluatable": true,
        "isEvaluated": true,
        "hasEvaluationConfig": false
      }
    ]
  }
}
```

### 6. 获取项目角色枚举（字段过滤选项）
**请求**
```http
GET /psc/role/enum
```

**响应示例**
```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "fields": {
      "isEvaluatable": [
        { "label": "是", "value": true },
        { "label": "否", "value": false }
      ],
      "isEvaluated": [
        { "label": "是", "value": true },
        { "label": "否", "value": false }
      ],
      "disableFlag": [
        { "label": "正常", "value": false },
        { "label": "禁用", "value": true }
      ]
    }
  }
}
```

### 7. 删除项目角色
**请求**
```http
DELETE /psc/role/{ids}
```

**参数说明**
- `ids`: 支持单个ID或逗号分隔的多个ID

**响应示例**
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

### 8. 禁用/反禁用项目角色
**请求**
```http
PATCH /psc/role/{ids}
Content-Type: application/json

{
  "disableFlag": true
}
```

**参数说明**
- `ids`: 单个ID或逗号分隔的多个ID
- `disableFlag`: true=禁用, false=反禁用

**响应示例**
```json
{
  "code": 200,
  "message": "禁用成功",
  "data": null
}
```

---

## 权限验证流程

### 前端权限控制
项目角色模块在 PSC 系统中属于基础配置模块，权限控制相对简单：

1. **页面访问权限**：通过路由元信息配置（hidden: true，通过菜单控制）
2. **操作权限**：
   - 新增/修改/删除：基于用户角色权限
   - 禁用操作：需要相应业务权限

### 后端权限验证
- PSC 系统采用统一的 RBAC 权限模型
- 角色操作需要具备 `psc:role:{operation}` 权限
- 禁用操作可能检查角色是否在项目模板中被使用

---

## 认证与授权区别说明

### 认证 (Authentication)
- 用户登录后获取 Token
- 所有 API 请求通过 `Authorization: Bearer {token}` 头携带认证信息
- 项目角色模块不涉及独立的认证逻辑

### 授权 (Authorization)
- **业务授权**：`isEvaluatable` / `isEvaluated` 定义角色在评价体系中的权限
- **系统授权**：基于 RBAC 的操作权限控制（增删改查）
- **数据授权**：用户只能看到有权访问的角色数据

---

## 与其他模块关系

### 依赖关系图
```
ProjectRole (项目角色)
    ↓
    ├── NodeDefinition (节点定义)
    │   └── projectRoleId: 项目角色ID
    │
    ├── EvaluationConfig (评价配置)
    │   └── projectRoleId: 项目角色ID
    │   └── name: 角色名称（冗余）
    │   └── isEvaluatable/isEvaluated: 继承自角色
    │
    ├── ProjectTemplate (项目模板)
    │   └── 节点配置中的负责人关联项目角色
    │
    └── ProjectInstance (项目实例)
        └── 项目成员关联项目角色
```

### 模块间数据流转
1. **项目角色 → 节点定义**：节点定义通过下拉选择项目角色，保存 `projectRoleId`
2. **项目角色 → 评价配置**：评价配置选择角色后，自动带出 `isEvaluatable` / `isEvaluated` 属性
3. **项目角色 → 项目模板**：模板节点配置负责人时，从项目角色列表选择

---

## 常见业务场景

### 场景 1：创建新的项目角色
**流程**：
1. 用户点击"新增"按钮
2. 填写角色名称（必填）
3. 选择是否参与评价/是否被评价
4. 点击保存，后端自动生成角色编码
5. 保存成功后跳转到编辑页面

### 场景 2：配置角色的评价属性
**业务规则**：
- 项目经理：通常参与评价、也被评价
- 普通成员：通常参与评价、也被评价
- 外部顾问：通常被评价、但不参与评价他人

### 场景 3：禁用项目角色
**注意事项**：
- 禁用前需检查角色是否在项目模板中被使用
- 禁用后，节点定义中该角色仍可见，但不可选择
- 已创建的项目实例不受影响

### 场景 4：批量操作
**支持操作**：
- 批量删除（通过多选选择）
- 批量禁用/反禁用

---

## 技术实现建议（Django）

### 模型定义
```python
from django.db import models

class ProjectRole(models.Model):
    """项目角色模型"""
    code = models.CharField(max_length=50, unique=True, verbose_name="角色编码")
    name = models.CharField(max_length=100, verbose_name="角色名称")
    is_evaluatable = models.BooleanField(default=True, verbose_name="是否参与评价")
    is_evaluated = models.BooleanField(default=True, verbose_name="是否被评价")
    disable_flag = models.BooleanField(default=False, verbose_name="是否禁用")
    creator = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'psc_project_role'
        verbose_name = '项目角色'
        verbose_name_plural = '项目角色'

    def __str__(self):
        return self.name
```

### 序列化器
```python
from rest_framework import serializers

class ProjectRoleSerializer(serializers.ModelSerializer):
    has_evaluation_config = serializers.SerializerMethodField()

    class Meta:
        model = ProjectRole
        fields = '__all__'

    def get_has_evaluation_config(self, obj):
        """检查是否已有评价配置"""
        return hasattr(obj, 'evaluation_config') and obj.evaluation_config.exists()
```

### 视图集
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class ProjectRoleViewSet(viewsets.ModelViewSet):
    """项目角色视图集"""
    queryset = ProjectRole.objects.all()
    serializer_class = ProjectRoleSerializer

    def perform_create(self, serializer):
        """创建时自动生成编码"""
        role = serializer.save()
        if not role.code:
            role.code = self.generate_code(role)
            role.save()

    @action(detail=False, methods=['get'])
    def simple(self, request):
        """简单列表（供下拉选择）"""
        roles = self.queryset.filter(disable_flag=False)
        serializer = self.get_serializer(roles, many=True)
        return Response({'items': serializer.data})

    @action(detail=False, methods=['get'])
    def enum(self, request):
        """枚举查询"""
        return Response({
            'fields': {
                'isEvaluatable': [
                    {'label': '是', 'value': True},
                    {'label': '否', 'value': False}
                ],
                'isEvaluated': [
                    {'label': '是', 'value': True},
                    {'label': '否', 'value': False}
                ]
            }
        })

    @action(detail=True, methods=['patch'])
    def set_disable(self, request, pk=None):
        """禁用/反禁用"""
        role = self.get_object()
        disable_flag = request.data.get('disableFlag', False)
        role.disable_flag = disable_flag
        role.save()
        return Response({'message': f'{"禁用" if disable_flag else "反禁用"}成功'})
```

---

## 扩展设计策略

### 1. 角色分类体系
**未来扩展**：支持角色分类（管理层、执行层、外部角色等）
```javascript
{
  category: "management", // management | execution | external
  level: 1 // 角色层级
}
```

### 2. 角色技能标签
**未来扩展**：为角色添加技能标签，用于智能分配
```javascript
{
  skills: ["Java", "Vue.js", "Project Management"]
}
```

### 3. 角色模板
**未来扩展**：预定义角色模板，快速创建常用角色
```javascript
{
  template: "project_manager", // 预设模板
  customFields: {} // 自定义字段
}
```

---

## 演进方向 (Future Evolution)

### 短期演进（1-3个月）
1. **角色使用统计**：统计角色在项目模板中的使用次数
2. **角色推荐**：基于历史数据推荐常用角色
3. **角色导入导出**：支持批量导入角色配置

### 中期演进（3-6个月）
1. **角色权限矩阵**：可视化展示角色的评价权限关系
2. **角色版本管理**：支持角色配置的版本控制
3. **角色继承体系**：支持角色继承，子角色继承父角色的评价属性

### 长期演进（6个月以上）
1. **智能角色推荐**：基于项目特征推荐合适的角色组合
2. **角色能力画像**：结合员工数据，为每个角色构建能力画像
3. **跨项目角色分析**：分析角色在不同项目中的表现

---

## 特有名词索引

当以下名词出现时，应快速定位到本技能：

| 名词 | 定位 |
|------|------|
| 项目角色 | 本模块核心实体 |
| ProjectRole | 本模块英文名称 |
| 角色编码 | 角色的唯一标识字段 |
| isEvaluatable | 角色参与评价属性 |
| isEvaluated | 角色被评价属性 |
| 禁用角色 | 业务状态管理功能 |
| projectrole | 前端路由/文件命名 |
| 简单角色列表 | 下拉选项接口 |
| 角色评价配置 | 角色与评价配置的关联 |
| 节点负责人 | 节点定义中的角色关联 |

---

## 前端文件映射

### 页面组件
- `src/views/psc/projectrole/index.vue` - 角色列表页
- `src/views/psc/projectrole/add.vue` - 角色新增页
- `src/views/psc/projectrole/edit.vue` - 角色编辑页
- `src/views/psc/projectrole/components/roleRender.vue` - 角色表单组件

### API 接口
- `src/api/pm/projectrole.js` - 角色相关 API（注意：PM 和 PSC 共用此文件）

### 路由配置
- `src/router/modules/psc.js` - PSC 路由模块中包含项目角色路由
