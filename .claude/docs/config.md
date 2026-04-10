# Config Module

## 概述

`config` 模块负责从 YAML 配置文件加载和解析 Symlink-Hub 的配置信息。配置文件定义了内容库位置、项目列表、agent 规则等核心信息。

## 配置文件格式

配置文件默认为 `symlink-hub.config.yaml`：

```yaml
contentRoot: ./fixtures/content
stateRoot: ./.symlink-hub
defaultMode: symlink

agents:
  codex:
    agentFileName: CODEX.md
    roots:
      skill: .codex/skills
      rule: .codex/rules
      doc: .codex/docs
      command: .codex/commands

projects:
  - name: backend
    path: ./fixtures/projects/backend
    agents:
      - codex
    includeTags:
      - global
      - backend
    excludeTags:
      - experimental
    mode: symlink
    conflict: replace
```

## 核心类型

### Config

根配置结构：

```go
type Config struct {
    ContentRoot string                 // 内容库根目录
    StateRoot   string                 // 状态文件存储目录
    DefaultMode string                 // 默认分发模式
    Agents      map[string]AgentConfig // Agent 配置映射
    Projects    []ProjectConfig        // 项目配置列表
}
```

### AgentConfig

单个 Agent 的配置：

```go
type AgentConfig struct {
    AgentFileName string            // Agent 文件名（如 CODEX.md）
    Roots         map[string]string // 内容类型到输出路径的映射
}
```

**Roots 映射表**：
| 键 | 值示例 | 说明 |
|---|--------|------|
| `skill` | `.codex/skills` | skill 类型内容的输出目录 |
| `rule` | `.codex/rules` | rule 类型内容的输出目录 |
| `doc` | `.codex/docs` | doc 类型内容的输出目录 |
| `command` | `.codex/commands` | command 类型内容的输出目录 |

### ProjectConfig

单个项目的配置：

```go
type ProjectConfig struct {
    Name        string   // 项目名称（唯一标识）
    Path        string   // 项目文件系统路径
    Agents      []string // 该项目使用的 agent 列表
    IncludeTags []string // 包含的标签（白名单）
    ExcludeTags []string // 排除的标签（黑名单）
    Features    []string // 项目特性标签（预留）
    Mode        string   // 分发模式（覆盖默认值）
    Conflict    string   // 冲突处理策略
}
```

## 使用方式

### Loader

配置加载器：

```go
loader := config.NewLoader("symlink-hub.config.yaml")
cfg, err := loader.Load()
if err != nil {
    log.Fatal(err)
}
```

**Load() 方法执行的操作**：
1. 读取配置文件
2. 解析 YAML 格式
3. 设置默认值
4. 将相对路径转换为绝对路径
5. 验证配置完整性

### 路径解析规则

- 相对于配置文件目录的路径会被转换为绝对路径
- `ContentRoot` 和 `StateRoot` 支持相对路径
- 项目 `Path` 支持相对路径

### 配置验证

加载时会验证：
- `ContentRoot` 不能为空
- 至少定义一个 agent
- 每个 agent 必须有 `AgentFileName` 和至少一个 root
- 每个项目必须有 `Name`、`Path` 和至少一个 agent

## 设计决策

1. **无依赖 YAML 解析**：手动解析 YAML，避免外部依赖
2. **绝对路径优先**：内部统一使用绝对路径，避免相对路径混乱
3. **默认值机制**：项目可省略 `Mode` 和 `Conflict`，使用全局默认值

## 扩展配置

如需支持新的内容类型，在 `AgentConfig.Roots` 中添加映射：

```yaml
agents:
  codex:
    roots:
      # 新增类型
      template: .codex/templates
```

然后在 `mapper` 模块中添加对应的路径映射逻辑。
