# Core Module

## 概述

`core` 模块定义了 Symlink-Hub 项目的核心数据类型和常量。这些类型在整个项目中被广泛使用，是系统的基础数据模型。

## 核心类型

### ContentType

内容类型枚举，定义了所有支持的内容类型：

```go
type ContentType string

const (
    ContentTypeAgent    ContentType = "agent"
    ContentTypeSkill    ContentType = "skill"
    ContentTypeRule     ContentType = "rule"
    ContentTypeDoc      ContentType = "doc"
    ContentTypeCommand  ContentType = "command"
)
```

**用途**：标识内容项的类型，决定其在目标项目中的输出路径。

### ContentItem

单个内容项的完整表示：

```go
type ContentItem struct {
    ID           string      // 唯一标识符
    Title        string      // 显示标题
    Type         ContentType // 内容类型
    Targets      []string    // 适用的 agent 列表
    Tags         []string    // 标签（用于项目过滤）
    Projects     []string    // 显式指定的项目列表
    Weight       int         // 优先级权重
    Status       string      // 状态（active/inactive）
    SourcePath   string      // 源文件路径（运行时注入）
    Checksum     string      // 内容校验和（运行时生成）
    LastModified string      // 最后修改时间（运行时生成）
}
```

**字段说明**：
- `ID`：内容项的唯一标识符，必须全局唯一
- `Type`：决定内容在目标项目中的输出位置
- `Targets`：为空时表示所有 agent 可用，否则必须包含当前 agent
- `Projects`：为空时表示所有项目可用，否则必须包含当前项目名
- `Tags`：用于项目的 includeTags/excludeTags 过滤

### BuildAction

构建操作类型：

```go
type BuildAction string

const (
    BuildActionCreate    BuildAction = "create"
    BuildActionReplace   BuildAction = "replace"
    BuildActionSkip      BuildAction = "skip"
    BuildActionConflict  BuildAction = "conflict"
    BuildActionDelete    BuildAction = "delete"
)
```

**用途**：标识对目标文件应该执行的操作。

### BuildPlanEntry

构建计划中的单个条目：

```go
type BuildPlanEntry struct {
    Action      BuildAction // 要执行的操作
    ProjectName string      // 目标项目名
    Agent       string      // 目标 agent
    SourceItems []string    // 源文件路径列表
    OutputPath  string      // 输出路径
    Mode        string      // 分发模式（symlink/copy）
    Reason      string      // 操作原因（冲突时）
}
```

### BuildPlan

完整的构建计划：

```go
type BuildPlan struct {
    GeneratedAt string          // 生成时间（ISO 8601）
    Entries     []BuildPlanEntry // 计划条目列表
}
```

**用途**：描述一次同步操作的所有变更，用于 dry-run 预览和实际执行。

### DistributionMode & ConflictStrategy

分发模式和冲突处理策略：

```go
type DistributionMode string

const (
    DistributionModeSymlink DistributionMode = "symlink"
    DistributionModeCopy    DistributionMode = "copy"
)

type ConflictStrategy string

const (
    ConflictStrategySkip    ConflictStrategy = "skip"
    ConflictStrategyReplace ConflictStrategy = "replace"
    ConflictStrategyBackup  ConflictStrategy = "backup"
)
```

## 设计原则

1. **不可变性**：类型定义本身不包含业务逻辑，保持纯数据结构
2. **运行时分离**：运行时生成的字段（如 SourcePath）与源数据字段分离
3. **显式优于隐式**：使用枚举类型而非字符串字面量，提高类型安全

## 使用示例

```go
// 创建内容项
item := core.ContentItem{
    ID:      "auth-login",
    Title:   "Auth Login Skill",
    Type:    core.ContentTypeSkill,
    Targets: []string{"codex", "claude"},
    Tags:    []string{"backend", "auth"},
    Status:  "active",
}

// 创建构建计划
plan := &core.BuildPlan{
    GeneratedAt: time.Now().Format(time.RFC3339),
    Entries: []core.BuildPlanEntry{
        {
            Action:      core.BuildActionCreate,
            ProjectName: "backend",
            Agent:       "codex",
            OutputPath:  "/path/to/project/.codex/skills/auth-login.md",
            Mode:        string(core.DistributionModeSymlink),
        },
    },
}
```
