# PSC 评价配置模块 (EvaluationConfig)

## 模块定位

PSC 评价配置模块是项目模板系统的核心组成部分，负责定义项目中各角色的评价规则与标准。该模块与项目角色(ProjectRole)模块紧密关联，为每个角色配置评价项、评价内容、评价等级和分值，支撑项目实施过程中的角色评价与绩效考核。

**核心职责**：为可被评价的项目角色配置评价体系，包括评价项(维度)、评价内容(等级/标准/分值)、以及开放评价权限的角色范围。

## 模块职责边界

### 核心功能边界
- **角色评价配置管理**：为 `isEvaluated=true` 的项目角色创建评价配置
- **评价项管理**：配置评价维度(如"工作质量"、"沟通能力"等)
- **评价内容管理**：为每个评价项配置评价等级(如"优秀"、"良好")、评价标准描述和分值
- **开放评价角色配置**：指定哪些角色可以对该角色进行评价
- **贡献度提示语**：配置项目贡献度填写的提示文本

### 模块边界说明
- **不负责**：角色本身的创建与管理(由 ProjectRole 模块负责)
- **不负责**：具体的评价执行与记录(由项目执行阶段的评价功能负责)
- **不负责**：评价结果统计与分析(由报表模块负责)

## 核心数据模型

### 1. EvaluationConfig (评价配置主表)
```typescript
{
  id: string;                      // 配置ID
  projectRoleId: string;           // 关联的项目角色ID
  projectRoleName: string;         // 项目角色名称(冗余)
  isEvaluatable: boolean;          // 是否参与评价(继承自角色)
  isEvaluated: boolean;            // 是否被评价(继承自角色)
  contributionTips: string;        // 项目贡献度提示语
  remark: string;                  // 备注
  creator: string;                 // 创建人
  createTime: string;              // 创建时间
  updateTime: string;              // 更新时间
  items: EvaluationItem[];         // 评价项列表
}
```

### 2. EvaluationItem (评价项)
```typescript
{
  id: string;                      // 评价项ID
  name: string;                    // 评价项名称(如"工作质量")
  isEvaluated: boolean;            // 是否参与评价
  remark: string;                  // 备注
  roles: ProjectRole[];            // 可评价此项目的角色列表
  options: EvaluationOption[];     // 评价内容选项
  createTime: string;
  updateTime: string;
}
```

### 3. EvaluationOption (评价内容/选项)
```typescript
{
  id: string;                      // 选项ID
  name: string;                    // 评价等级(如"优秀"、"良好")
  description: string;             // 评价标准描述
  score: number;                   // 分值(0-100)
  createTime: string;
  updateTime: string;
}
```

## 权限验证流程

### 角色关联验证
```
1. 只有 isEvaluated=true 的项目角色才能创建评价配置
2. 创建评价配置后，该角色在列表中被标记(hasEvaluationConfig=true)
3. 已有评价配置的角色不会出现在新增页面的角色选择器中
```

### 角色互斥逻辑
```
- 开放评价角色中不能包含当前被评价角色自己
- 只有 isEvaluatable=true 的角色才能被选为"开放评价角色"
```

### 字段只读控制
```
- isEvaluatable/isEvaluated: 从项目角色继承，不可编辑
- projectRoleName: 创建后不可更改(保证数据一致性)
```

## 认证与授权区别说明

### 认证 (Authentication)
- 系统级别的用户身份验证，由全局登录态管理
- 本模块依赖全局认证状态，无需额外认证逻辑

### 授权 (Authorization)
- **数据级授权**：用户只能查看/编辑自己创建或有权限的评价配置
- **功能级授权**：
  - 新增/编辑权限：`permitStatus.disabled`
  - 删除权限：`permitStatus.deletePermission`
- **角色级授权**：只有项目成员才能参与项目评价

## 与其他模块关系

### 依赖关系 (Dependency)
```
ProjectRole (项目角色)
    ↓ 1:N 关联
EvaluationConfig (评价配置)
    ↓ 1:N 关联
EvaluationItem (评价项)
    ↓ 1:N 关联
EvaluationOption (评价内容)
```

### 数据流向
```
ProjectRole.isEvaluated = true
    ↓
创建 EvaluationConfig (配置评价体系)
    ↓
项目实施阶段调用评价配置
    ↓
生成评价记录 (EvaluationRecord)
```

### 模块协作
- **ProjectRole 模块**：提供角色基础信息，决定角色是否可被评价
- **NodeDefinition 模块**：节点定义可能引用评价配置进行节点评价
- **ProjectTemplate 模块**：项目模板包含完整的角色与评价配置体系

## 常见业务场景

### 1. 创建角色评价配置
**场景**：为新增的"项目经理"角色配置评价体系
**流程**：
1. 选择角色名称(只显示 isEvaluated=true 且无评价配置的角色)
2. 自动带出 isEvaluatable/isEvaluated 字段
3. 填写贡献度提示语
4. 新增评价项(如"工作质量"、"团队协作")
5. 为每个评价项配置评价等级和分值
6. 选择可评价此项目的角色(如"项目总监"、"客户代表")

### 2. 编辑评价配置
**场景**：调整现有角色的评价标准
**流程**：
1. 修改评价项名称/描述
2. 调整评价等级和分值
3. 增减可评价角色
4. 系统自动对比原始数据，仅提交变更项

### 3. 删除评价配置
**场景**：角色不再需要评价功能
**约束**：
- 删除后角色可重新创建评价配置
- 建议先禁用而非直接删除(保留历史数据)

### 4. 评价内容管理
**场景**：为"工作质量"评价项配置等级
**配置示例**：
- 优秀(90-100分)：超出预期，质量卓越
- 良好(80-89分)：符合预期，质量可靠
- 合格(60-79分)：基本达标，需改进
- 不合格(0-59分)：未达标，需重做

## 技术实现建议

### 前端组件结构
```
src/views/psc/evaluationconfig/
├── index.vue              # 列表页
├── add.vue                # 新增页
├── edit.vue               # 编辑页
└── components/
    └── evalutationRender.vue  # 评价配置表单组件(复用)
```

### 核心组件逻辑
**evalutationRender.vue 组件职责**：
- 基础信息表单(角色选择、贡献度提示)
- 评价项管理表格(动态增删行)
- 评价内容管理表格(基于选中评价项动态展示)
- 数据对比与变更检测
- 表单校验与提交

### 关键技术点
1. **表格行点击切换**：点击评价项行，下方展示对应的评价内容
2. **数据快照对比**：记录原始数据，仅提交变更项
3. **联动过滤**：角色选择器自动排除已有配置的角色
4. **防重复提交**：使用 debounce 处理保存操作

### API 接口规范

#### 获取评价配置列表
```http
GET /psc/evaluation
Query: {
  name?: string;        # 角色名称(模糊搜索)
  nodeName?: string;    # 节点名称(预留)
  pageNum: number;
  pageSize: number;
}
Response: {
  data: EvaluationConfig[];
  total: number;
}
```

#### 获取评价配置详情
```http
GET /psc/evaluation/{id}
Response: {
  data: {
    id: string;
    projectRoleId: string;
    projectRoleName: string;
    isEvaluatable: boolean;
    isEvaluated: boolean;
    contributionTips: string;
    remark: string;
    items: Array<{
      id: string;
      name: string;
      isEvaluated: boolean;
      remark: string;
      roles: Array<{ id: string; name: string }>;
      options: Array<{
        id: string;
        name: string;
        description: string;
        score: number;
      }>;
    }>;
  }
}
```

#### 新增评价配置
```http
POST /psc/evaluation
Body: {
  projectRoleId: string;
  contributionTips?: string;
  remark?: string;
  itemData: Array<{
    name: string;
    isEvaluated: boolean;
    roleData: string[];  # 可评价角色ID列表
    optionData: Array<{
      name: string;      # 等级
      score: number;
      description: string;
    }>;
  }>;
}
Response: {
  data: { insertId: string };
}
```

#### 更新评价配置
```http
PUT /psc/evaluation/{id}
Body: {
  projectRoleId?: string;
  contributionTips?: string;
  remark?: string;
  itemData: Array<{
    id?: string;         # 有id表示修改，无id表示新增
    deleted?: boolean;   # true表示删除
    name?: string;
    isEvaluated?: boolean;
    roleData?: string[];
    optionData?: Array<{
      id?: string;       # 有id表示修改，无id表示新增
      name?: string;
      score?: number;
      description?: string;
    }>;
  }>;
}
```

#### 删除评价配置
```http
DELETE /psc/evaluation/{id}
```

### 字典枚举
```javascript
// 前端字典类型
dict.type.isEvaluatable  // 是否参与评价: {label: '是', value: true}, {label: '否', value: false}
dict.type.isEvaluated    // 是否被评价: {label: '是', value: true}, {label: '否', value: false}
```

## 扩展设计策略

### 1. 评价模板化
未来可将常用评价配置抽象为模板，支持快速复用：
```
- 技术岗位评价模板
- 管理岗位评价模板
- 支持岗位评价模板
```

### 2. 评价权重配置
支持为不同评价项配置权重，实现加权计算总分：
```typescript
{
  id: string;
  name: string;
  weight: number;  // 权重百分比
  options: EvaluationOption[];
}
```

### 3. 多维度评价
支持同一评价项的多个维度：
```typescript
{
  id: string;
  name: string;  // "工作质量"
  dimensions: [
    { name: "代码质量", weight: 0.4 },
    { name: "文档质量", weight: 0.3 },
    { name: "交付及时性", weight: 0.3 }
  ];
}
```

### 4. 评价历史追踪
记录评价配置的变更历史，支持版本对比：
```typescript
{
  configId: string;
  version: number;
  changeLog: string;
  operator: string;
  changeTime: string;
}
```

## 演进方向 (Future Evolution)

### 短期优化
1. **批量导入导出**：支持评价配置的 Excel 导入导出
2. **配置复制**：基于现有配置快速创建新角色的评价体系
3. **智能推荐**：根据角色类型推荐评价项模板

### 中期规划
1. **动态评价表单**：根据项目类型动态调整评价项
2. **评价流程编排**：定义评价的触发时机与流转规则
3. **评价数据分析**：统计评价结果，生成角色绩效报告

### 长期愿景
1. **AI 辅助评价**：基于项目数据自动生成评价建议
2. **360度评价体系**：整合上级、下级、同事、客户的多维评价
3. **能力画像**：基于历史评价数据生成角色能力模型

## 模块特有名词索引

当用户提到以下术语时，应定位到本模块：

| 术语 | 说明 |
|------|------|
| 评价配置 | 本模块核心功能 |
| 评价项 | 评价维度，如"工作质量" |
| 评价内容 | 具体的评价等级、标准和分值 |
| 评价等级 | 如"优秀"、"良好" |
| 评价标准 | 每个等级的详细描述 |
| 分值 | 对应等级的数值评分 |
| 开放评价角色 | 有权对该角色进行评价的角色列表 |
| isEvaluatable | 是否参与评价(主动评价他人) |
| isEvaluated | 是否被评价(接受他人评价) |
| 贡献度提示语 | 项目贡献度填写的提示文本 |
| hasEvaluationConfig | 角色是否已有评价配置 |

## 常见问题排查

### Q1: 角色选择器为空？
- 检查角色是否设置 `isEvaluated=true`
- 检查角色是否已有评价配置

### Q2: 无法新增评价内容？
- 需要先选中一个评价项(点击表格行)
- 检查是否处于编辑模式(`permitStatus.disabled`)

### Q3: 提示"无任何修改项"？
- 系统对比原始数据与当前数据
- 确保至少有一个字段发生了变更
