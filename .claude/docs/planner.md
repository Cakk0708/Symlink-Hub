# Planner Module

## 概述

`planner` 模块负责生成构建计划（Build Plan）。根据选中的内容项、项目配置和当前文件系统状态，决定每个文件应该执行的操作类型。

## 核心功能

### Planner

构建计划生成器：

```go
planner := planner.NewPlanner(cfg)
plan, err := planner.GeneratePlan(items, projectName, agentName)
```

### PrintPlan

打印构建计划（可读格式）：

```go
planner.PrintPlan(plan)
```

## 构建计划生成流程

```
┌──────────────────┐
│  选中内容项列表   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  检查 Agent 冲突  │
│  (多个 agent 文件) │
└────────┬─────────┘
         │
    有冲突 │ 无冲突
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌──────────────┐
│ 冲突 │  │  逐项处理    │
│计划  │  │  每个内容项  │
└──────┘  └──────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ 调用 Mapper   │
         │ 获取输出路径  │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ 检查文件状态  │
         │ 决定 Action   │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ 生成计划条目  │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │  返回完整计划  │
         └───────────────┘
```

## Action 决策逻辑

### 1. Agent 冲突检测

如果选中多个 `type: agent` 的内容项：

```go
if len(agentItems) > 1 {
    // 返回冲突计划
    return conflictPlan
}
```

**冲突计划示例**：
```
CONFLICTS (2):
  ! /path/to/CODEX.md - multiple agent items defined for this project
```

### 2. 文件存在性检查

```go
if _, err := os.Stat(outputPath); os.IsNotExist(err) {
    return BuildActionCreate  // 文件不存在 → 创建
}
```

### 3. 文件类型检查

```go
if info, err := os.Lstat(outputPath); err == nil {
    if info.Mode()&os.ModeSymlink != 0 {
        return BuildActionReplace  // 已是符号链接 → 替换
    }
}
```

### 4. 冲突策略应用

根据项目配置的 `conflict` 策略：

| 策略 | 行为 |
|------|------|
| `skip` | 跳过，不修改现有文件 |
| `replace` | 替换现有文件 |
| `backup` | 备份后替换（未实现） |

```go
switch proj.Conflict {
case "replace":
    return BuildActionReplace
case "skip":
    return BuildActionSkip
default:
    return BuildActionSkip
}
```

## 输出格式

### Dry-Run 输出示例

```
Build Plan (generated at 2026-04-10T04:31:30Z)
------------------------------------------------------------

CREATE (3):
  + /home/user/backend/CODEX.md
  + /home/user/backend/.codex/skills/auth-login.md
  + /home/user/backend/.codex/rules/commit-format.md

REPLACE (1):
  ~ /home/user/backend/.codex/skills/api-client.md

CONFLICTS (1):
  ! /home/user/backend/CODEX.md - multiple agent items defined

Total: 5 actions
```

## BuildPlan 结构

```go
type BuildPlan struct {
    GeneratedAt string
    Entries     []BuildPlanEntry
}

type BuildPlanEntry struct {
    Action      BuildAction
    ProjectName string
    Agent       string
    SourceItems []string
    OutputPath  string
    Mode        string
    Reason      string  // 仅冲突时有值
}
```

## 使用示例

```go
// 创建 planner
planner := planner.NewPlanner(cfg)

// 生成计划
plan, err := planner.GeneratePlan(selectedItems, "backend", "codex")
if err != nil {
    log.Fatal(err)
}

// 打印计划
planner.PrintPlan(plan)

// 检查是否有冲突
hasConflicts := false
for _, entry := range plan.Entries {
    if entry.Action == core.BuildActionConflict {
        hasConflicts = true
        break
    }
}

if hasConflicts {
    fmt.Println("Warning: Conflicts detected!")
}
```

## 错误处理

| 错误情况 | 处理方式 |
|----------|----------|
| 项目不存在 | 返回错误 |
| 路径映射失败 | 返回错误 |
| 文件系统访问错误 | 返回错误 |

## 设计原则

1. **描述性**：计划是纯描述性的，不执行任何文件操作
2. **可审查**：计划可以打印供人工审查
3. **原子性**：计划要么完全执行，要么完全不执行
4. **幂等性**：多次生成相同输入的计划应该一致
