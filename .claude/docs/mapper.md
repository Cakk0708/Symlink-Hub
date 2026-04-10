# Mapper Module

## 概述

`mapper` 模块负责将内容项映射到目标项目中的具体输出路径。根据内容类型、agent 配置和项目路径，计算出文件应该存放的位置。

## 核心功能

### Mapper

路径映射器：

```go
mapper := mapper.NewMapper(cfg)
outputPath, err := mapper.MapOutputPath(item, projectName, agentName)
```

### GetProject

获取项目配置：

```go
proj, err := mapper.GetProject(projectName)
```

## 路径映射规则

### Agent 类型

映射到项目根目录的 agent 文件：

```
{项目路径}/{AgentFileName}
```

示例：
```
/home/user/backend/CODEX.md
```

### Skill 类型

映射到 agent 的 skills 目录：

```
{项目路径}/{roots.skill}/{id}.md
```

示例：
```
/home/user/backend/.codex/skills/auth-login.md
```

### Rule 类型

映射到 agent 的 rules 目录：

```
{项目路径}/{roots.rule}/{id}.md
```

示例：
```
/home/user/backend/.codex/rules/commit-format.md
```

### Doc 类型

映射到 agent 的 docs 目录：

```
{项目路径}/{roots.doc}/{id}.md
```

示例：
```
/home/user/backend/.codex/docs/api.md
```

### Command 类型

映射到 agent 的 commands 目录：

```
{项目路径}/{roots.command}/{id}.md
```

示例：
```
/home/user/backend/.codex/commands/deploy.md
```

## 配置示例

### Agent Roots 配置

```yaml
agents:
  codex:
    agentFileName: CODEX.md
    roots:
      skill: .codex/skills
      rule: .codex/rules
      doc: .codex/docs
      command: .codex/commands
```

### 项目配置

```yaml
projects:
  - name: backend
    path: /home/user/backend
```

## 映射示例

| 内容类型 | ID | Agent | 项目 | 输出路径 |
|----------|----|----|----|----------|
| agent | codex-base | codex | backend | `/home/user/backend/CODEX.md` |
| skill | auth-login | codex | backend | `/home/user/backend/.codex/skills/auth-login.md` |
| rule | commit-format | codex | backend | `/home/user/backend/.codex/rules/commit-format.md` |
| doc | api-ref | claude | frontend | `/home/user/frontend/.claude/docs/api-ref.md` |
| command | deploy | codex | backend | `/home/user/backend/.codex/commands/deploy.md` |

## 错误处理

| 错误情况 | 错误信息 |
|----------|----------|
| 项目不存在 | `project not found: {name}` |
| Agent 不存在 | `unknown agent: {name}` |
| Agent 不支持该类型 | `agent {name} does not support {type} type` |
| 未知内容类型 | `unknown content type: {type}` |

## 扩展新类型

如需支持新的内容类型，按以下步骤操作：

### 1. 在 core/types.go 添加类型

```go
const (
    ContentTypeTemplate ContentType = "template"
)
```

### 2. 在 agent 配置添加 root

```yaml
agents:
  codex:
    roots:
      template: .codex/templates
```

### 3. 在 mapper 添加映射逻辑

```go
case core.ContentTypeTemplate:
    root, ok := agentCfg.Roots["template"]
    if !ok {
        return "", fmt.Errorf("agent %s does not support template type", agentName)
    }
    return filepath.Join(proj.Path, root, item.ID+".md"), nil
```

## 设计原则

1. **配置驱动**：路径规则由配置文件定义，不硬编码
2. **类型安全**：使用枚举类型，避免字符串拼写错误
3. **错误明确**：不支持的配置会立即返回明确的错误
4. **可扩展性**：新类型添加不影响现有逻辑
