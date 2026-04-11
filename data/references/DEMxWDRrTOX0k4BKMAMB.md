# 文档地图格式规范

> 按需读取此文件。在执行地图初始化、新增条目、更新链接时加载。

---

## 地图文件位置

```
docs/map/README.md     ← 主地图（必须存在）
```

---

## 主地图格式

```markdown
# 项目模块文档地图

> 最后更新：{YYYY-MM-DD}

本文件维护所有模块的文档索引，便于快速定位各模块的说明文档与接口文档。

---

## 模块索引

| App | 模块 | 说明 | 模块文档 | API 接口文档 |
|-----|------|------|----------|-------------|
| SM | Organization | 组织管理 | [📄 模块文档](../module/SM_Organization.md) | [🔌 接口文档](../api/SM_Organization.md) |
| SM | User | 用户管理 | [📄 模块文档](../module/SM_User.md) | [🔌 接口文档](../api/SM_User.md) |
| BDM | Project | 项目管理 | [📄 模块文档](../module/BDM_Project.md) | — |
```

---

## 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| App | Django app 名称 | `SM`、`BDM` |
| 模块 | Model / 功能模块名称 | `Organization` |
| 说明 | 模块一句话描述 | `组织管理` |
| 模块文档 | 指向 `docs/module/` 的相对链接 | `[📄 模块文档](../module/SM_Organization.md)` |
| API 接口文档 | 指向 `docs/api/` 的相对链接 | `[🔌 接口文档](../api/SM_Organization.md)` |

---

## 链接格式规范

- 使用**相对路径**，基于 `docs/map/README.md` 所在目录
- 模块文档链接前缀：`[📄 模块文档]`
- API 文档链接前缀：`[🔌 接口文档]`
- 文档尚未创建时填写：`—`（长破折号，非空格）

---

## 文件命名与链接对应关系

| 文档类型 | 文件路径规则 | 地图链接示例 |
|----------|------------|-------------|
| 模块文档 | `docs/module/{App}_{Model}.md` | `[📄 模块文档](../module/SM_Organization.md)` |
| API 文档 | `docs/api/{App}_{Model}.md` | `[🔌 接口文档](../api/SM_Organization.md)` |

---

## 新增条目示例

在表格末尾追加一行：

```markdown
| BDM | Contract | 合同管理 | [📄 模块文档](../module/BDM_Contract.md) | — |
```

若同时有 API 文档：

```markdown
| BDM | Contract | 合同管理 | [📄 模块文档](../module/BDM_Contract.md) | [🔌 接口文档](../api/BDM_Contract.md) |
```

---

## 更新链接示例

将已有条目中的 `—` 替换为实际链接：

**更新前：**
```markdown
| BDM | Contract | 合同管理 | [📄 模块文档](../module/BDM_Contract.md) | — |
```

**更新后：**
```markdown
| BDM | Contract | 合同管理 | [📄 模块文档](../module/BDM_Contract.md) | [🔌 接口文档](../api/BDM_Contract.md) |
```