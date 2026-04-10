# Manifest Module

## 概述

`manifest` 模块负责管理同步操作的清单文件。Manifest 记录每次同步的详细信息，用于状态查询、健康检查和清理操作。

## 核心功能

### Manager

Manifest 管理器：

```go
manifestMgr := manifest.NewManager(stateRoot)
```

### Write

写入 manifest：

```go
err := manifestMgr.Write(plan, projectName, agent)
```

**执行的操作**：
1. 创建 `stateRoot/manifests/` 目录
2. 将 BuildPlan 转换为 Manifest
3. 生成 ISO 8601 格式的时间戳
4. 写入 JSON 文件

### Read

读取 manifest：

```go
mft, err := manifestMgr.Read(projectName, agent)
```

### Remove

删除 manifest：

```go
err := manifestMgr.Remove(projectName, agent)
```

## Manifest 结构

### Manifest

```go
type Manifest struct {
    ProjectName string   // 项目名
    Agent       string   // Agent 名
    GeneratedAt string   // 生成时间 (ISO 8601)
    Mode        string   // 分发模式
    Entries     []Entry  // 清单条目
}
```

### Entry

```go
type Entry struct {
    SourceItemIDs []string // 源内容 ID 列表
    SourcePath    string   // 源文件路径
    OutputPath    string   // 输出路径
    Action        string   // 执行的操作
    Checksum      string   // 内容校验和
}
```

## 文件存储

### 存储位置

```
stateRoot/
└── manifests/
    ├── backend.codex.json
    ├── frontend.claude.json
    └── backend.claude.json
```

### 文件命名规则

```
{projectName}.{agentName}.json
```

### Manifest 示例

```json
{
  "projectName": "backend",
  "agent": "codex",
  "generatedAt": "2026-04-10T04:31:30Z",
  "mode": "symlink",
  "entries": [
    {
      "sourceItemIds": ["codex-base"],
      "sourcePath": "/repo/content/agent/codex-base.md",
      "outputPath": "/home/user/backend/CODEX.md",
      "action": "create",
      "checksum": "crc32:12345"
    },
    {
      "sourceItemIds": ["auth-login"],
      "sourcePath": "/repo/content/skill/auth-login.md",
      "outputPath": "/home/user/backend/.codex/skills/auth-login.md",
      "action": "create",
      "checksum": "crc32:67890"
    }
  ]
}
```

## 使用场景

### 1. Sync 后记录

```go
// 执行同步
if err := dist.ExecutePlan(plan); err != nil {
    return err
}

// 写入 manifest
if err := manifestMgr.Write(plan, proj.Name, agent); err != nil {
    log.Printf("Warning: failed to write manifest: %v", err)
}
```

### 2. Status 查询

```go
mft, err := manifestMgr.Read("backend", "codex")
if err != nil {
    // 未找到 manifest，可能未同步过
    return
}

fmt.Printf("Last sync: %s\n", mft.GeneratedAt)
fmt.Printf("Files: %d\n", len(mft.Entries))
fmt.Printf("Mode: %s\n", mft.Mode)
```

### 3. Clean 操作

```go
mft, err := manifestMgr.Read("backend", "codex")
if err != nil {
    fmt.Println("No manifest found")
    return
}

// 反向删除（先删除子文件，再删除父目录）
for i := len(mft.Entries) - 1; i >= 0; i-- {
    entry := mft.Entries[i]
    os.Remove(entry.OutputPath)
}

// 删除 manifest 文件
manifestMgr.Remove("backend", "codex")
```

### 4. Doctor 健康检查

```go
mft, err := manifestMgr.Read("backend", "codex")
if err != nil {
    return
}

for _, entry := range mft.Entries {
    // 检查文件是否存在
    if _, err := os.Stat(entry.OutputPath); os.IsNotExist(err) {
        fmt.Printf("Missing: %s\n", entry.OutputPath)
        continue
    }

    // 检查是否是符号链接
    if info, _ := os.Lstat(entry.OutputPath); info.Mode()&os.ModeSymlink != 0 {
        // 检查链接目标是否有效
        target, _ := os.Readlink(entry.OutputPath)
        if _, err := os.Stat(target); os.IsNotExist(err) {
            fmt.Printf("Broken symlink: %s -> %s\n", entry.OutputPath, target)
        }
    }
}
```

## 设计原则

1. **精确清理**：Manifest 记录确切的输出路径，支持精确删除
2. **状态追溯**：可以查询任意历史同步的状态
3. **健康检查**：通过对比 manifest 和实际文件系统检测漂移
4. **JSON 格式**：便于人工阅读和调试

## 注意事项

1. **并发安全**：当前实现不支持并发写入，需在外层加锁
2. **版本兼容**：Manifest 格式变更时需考虑向后兼容
3. **存储空间**：长时间运行会积累历史 manifest，考虑定期清理
4. **路径变更**：项目路径变更后旧 manifest 会失效
