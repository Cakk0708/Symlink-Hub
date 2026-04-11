# 文档地图格式规范

> 按需读取此文件。在执行地图初始化、新增条目、更新链接时加载。

---

## 文件位置

```
docs/map/README.md     ← 主地图（唯一入口）
```

地图中的所有路径均为**相对于 `docs/map/README.md` 所在目录**的相对路径：
- 模块说明文件 → `modules/{filename}.md`
- API 接口文件 → `api/{filename}.md`

---

## 文件命名规则

文件名格式：`{app小写}-{module_name}.md`

| App | 模块 | 模块文档文件名 | API文档文件名 |
|-----|------|--------------|-------------|
| BDM | customer | `bdm-customer.md` | `bdm-customer.md` |
| BDM | department | `bdm-department.md` | `bdm-department.md` |
| PM | project_log | `pm-project_log.md` | `pm-project_log.md` |
| SM | auth | `sm-auth.md` | `sm-auth.md` |
| PSC | node_definition | `psc-node_definition.md` | `psc-node_definition.md` |

---

## 地图条目格式

每个模块条目为一个列表项，`模块说明:` 和 `接口说明:` 作为缩进子行挂在条目下方：

```markdown
- `{route}/` - {模块名称}/{模块别名}
  - 模块说明: modules/{app}-{module}.md
  - 接口说明: api/{app}-{module}.md
```

**规则：**
- `模块说明:` 与 `接口说明:` 各占独立一行，缩进 2 个空格
- 路径后**不加括号、不加链接语法**，直接写纯文本路径
- 若某类文档尚未创建，**整行省略**（不写占位符）
- 同一条目可只有 `模块说明:` 或只有 `接口说明:`，也可两者都有

**示例（只有模块说明）：**
```markdown
- `customer/` - 客户管理
  - 模块说明: modules/bdm-customer.md
```

**示例（模块说明 + 接口说明都有）：**
```markdown
- `customer/` - 客户管理
  - 模块说明: modules/bdm-customer.md
  - 接口说明: api/bdm-customer.md
```

---

## 地图整体结构

地图按 app 分区，每个 app 为一个三级标题区块：

```markdown
# {项目名} 项目地图

本文档完整描述项目结构、模块命名、模块别名。

---

### {APP}（{App全称}）

{App 简介}

#### {子模块分组} - {分组说明}
- `{route}/` - {模块名称}
  - 模块说明: modules/{app}-{module}.md
- `{route}/{sub}/` - {子模块名称}
  - 模块说明: modules/{app}-{module}_{sub}.md
  - 接口说明: api/{app}-{module}_{sub}.md

**路由前缀：** `/{app_lower}/`
```

---

## 新增条目操作

在对应 app 区块、对应 `####` 分组下，找到路由位置插入新条目：

**新增前（条目不存在）：**
```markdown
#### log - 项目操作日志
- `log/` - 项目操作日志/项目日志/操作记录
```

**新增模块说明后：**
```markdown
#### log - 项目操作日志
- `log/` - 项目操作日志/项目日志/操作记录
  - 模块说明: modules/pm-project_log.md
```

**再次新增接口说明后：**
```markdown
#### log - 项目操作日志
- `log/` - 项目操作日志/项目日志/操作记录
  - 模块说明: modules/pm-project_log.md
  - 接口说明: api/pm-project_log.md
```

---

## 更新链接操作

条目已存在但路径有误或需要更新时，直接用 str_replace 替换对应行：

**替换前：**
```
  - 接口说明: api/pm-project_log_old.md
```

**替换后：**
```
  - 接口说明: api/pm-project_log.md
```

---

## 初始化地图模板

当 `docs/map/README.md` 完全不存在时，使用以下最小结构初始化，再插入当前模块条目：

```markdown
# 项目地图

本文档完整描述项目结构、模块命名、模块别名，涉及项目关键词必须在本文中找到对应模块。

---

### {APP}（{App全称}）

{App 简介}

#### {module} - {模块说明}
- `{route}/` - {模块名称}
  - {模块说明: modules/... 或 接口说明: api/...}

**路由前缀：** `/{app_lower}/`
```