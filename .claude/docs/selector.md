# Selector Module

## 概述

`selector` 模块负责内容选择逻辑。根据项目配置、agent 类型和内容属性，决定哪些内容项应该被分发到目标项目。

## 核心功能

### Selector

内容选择器：

```go
selector := selector.NewSelector(cfg)
selected := selector.Select(items, selector.Options{
    ProjectName: "backend",
    Agent:       "codex",
})
```

### Options

选择选项：

```go
type Options struct {
    ProjectName string // 目标项目名
    Agent       string // 目标 agent
}
```

## 选择逻辑

内容项被选中的条件（必须全部满足）：

### 1. 状态检查

```go
if item.Status != "" && item.Status != "active" {
    return false  // 非 active 状态的内容被跳过
}
```

### 2. 类型支持检查

所有 agent 默认支持以下类型：
- `agent`
- `skill`
- `rule`
- `doc`
- `command`

### 3. Targets 检查（Agent 过滤）

```go
// 如果内容指定了 targets，当前 agent 必须在其中
if len(item.Targets) > 0 {
    if !contains(item.Targets, agentName) {
        return false
    }
}
```

**规则**：
- `targets` 为空：所有 agent 可用
- `targets` 非空：指定的 agent 才能使用

### 4. Projects 检查（项目过滤）

```go
// 如果内容指定了 projects，当前项目必须在其中
if len(item.Projects) > 0 {
    if !contains(item.Projects, projectName) {
        return false
    }
}
```

**规则**：
- `projects` 为空：所有项目可用
- `projects` 非空：指定的项目才能使用

### 5. IncludeTags 检查（白名单）

```go
// 如果项目配置了 includeTags，内容必须至少匹配一个
if len(proj.IncludeTags) > 0 {
    hasMatch := false
    for _, tag := range item.Tags {
        if contains(proj.IncludeTags, tag) {
            hasMatch = true
            break
        }
    }
    if !hasMatch {
        return false
    }
}
```

**规则**：
- `includeTags` 为空：不过滤标签
- `includeTags` 非空：内容必须至少有一个匹配的标签

### 6. ExcludeTags 检查（黑名单）

```go
// 如果内容的标签在项目的 excludeTags 中，被排除
for _, tag := range item.Tags {
    if contains(proj.ExcludeTags, tag) {
        return false
    }
}
```

**规则**：
- 任何匹配 `excludeTags` 的内容都会被排除
- `excludeTags` 优先级高于 `includeTags`

## 决策流程图

```
                    ┌─────────────┐
                    │  开始检查   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
              No    │ Status =    │ Yes
              ┌─────┤ active?     ├─────┐
              │     └──────┬──────┘     │
              │            No            │
              │            │             │
              │       ┌────▼────┐        │
              │       │ 跳过    │        │
              │       └─────────┘        │
              │ Yes                      │
              │                          │
      ┌───────▼──────────┐              │
      │ 类型支持?         │              │
      └───────┬──────────┘              │
         No   │    Yes                   │
      ┌────────┴─────┐                  │
      │ 跳过          │                  │
      └───────────────┘                  │
                                         │
      ┌──────────────────────────────────┘
      │
      ▼
┌─────────────┐
│ Targets 检查│
│ (可选)      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Projects 检查│
│ (可选)      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ IncludeTags │
│ 检查(可选)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ ExcludeTags │
│ 检查(可选)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   选中      │
└─────────────┘
```

## 使用示例

### 示例 1：基本选择

```go
// 配置：项目 backend，agent codex
selected := selector.Select(items, Options{
    ProjectName: "backend",
    Agent:       "codex",
})
```

### 示例 2：标签过滤

项目配置：
```yaml
includeTags:
  - global
  - backend
excludeTags:
  - experimental
```

内容项：
```yaml
tags:
  - backend
  - auth
```

结果：✓ 选中（匹配 `backend`，不在排除列表）

内容项：
```yaml
tags:
  - experimental
  - backend
```

结果：✗ 跳过（在排除列表中）

### 示例 3：Targets 过滤

内容项：
```yaml
targets:
  - claude
```

选择选项：
```go
Options{Agent: "codex"}
```

结果：✗ 跳过（codex 不在 targets 中）

## 设计原则

1. **显式优于隐式**：默认允许，显式排除
2. **白名单优先**：includeTags 必须匹配，excludeTags 额外过滤
3. **组合灵活性**：多个过滤条件可以组合使用
4. **性能优化**：尽早返回失败，减少不必要的检查
