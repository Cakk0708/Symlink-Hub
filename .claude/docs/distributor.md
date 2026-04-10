# Distributor Module

## 概述

`distributor` 模块负责执行文件分发操作，将内容项实际创建或更新到目标项目中。支持 symlink 和 copy 两种分发模式。

## 核心功能

### Distributor

分发器：

```go
dist := distributor.NewDistributor(dryRun false)
```

**参数**：
- `dryRun`: true 时只打印不执行，false 时实际执行操作

### ExecutePlan

执行构建计划：

```go
err := dist.ExecutePlan(plan)
```

**执行流程**：
1. 遍历计划中的每个条目
2. 跳过 `Skip` 和 `Conflict` 操作
3. 根据条目的 Action 调用对应方法
4. 遇到错误立即返回

### DeleteFile

删除单个文件：

```go
err := dist.DeleteFile(path)
```

**附加功能**：
- 删除文件后尝试删除空目录
- 忽略文件不存在的错误

### CleanEntry

清理 manifest 条目：

```go
err := dist.CleanEntry(manifestEntry)
```

## 分发模式

### Symlink 模式

创建符号链接：

```go
func (d *Distributor) createSymlink(entry core.BuildPlanEntry) error
```

**行为**：
1. 确保目标目录存在
2. 删除现有文件/链接（如果存在）
3. 创建符号链接：`目标路径 -> 源文件路径`

**优点**：
- 内容更新后目标项目自动生效
- 节省磁盘空间
- 便于集中管理

**缺点**：
- 某些工具可能不支持符号链接
- 跨文件系统移动可能失效

### Copy 模式

复制文件内容：

```go
func (d *Distributor) createCopy(entry core.BuildPlanEntry) error
```

**行为**：
1. 确保目标目录存在
2. 删除现有文件（如果存在）
3. 复制源文件内容到目标

**优点**：
- 兼容性最好
- 文件独立，不受源影响

**缺点**：
- 内容更新需重新同步
- 占用更多磁盘空间

## 操作类型处理

| Action | 行为 |
|--------|------|
| `Create` | 创建新文件或链接 |
| `Replace` | 删除现有文件后创建 |
| `Skip` | 不执行任何操作 |
| `Conflict` | 不执行任何操作 |
| `Delete` | 删除文件（用于 clean） |

## 目录处理

### 自动创建目录

在创建文件前，确保目标目录存在：

```go
dir := filepath.Dir(entry.OutputPath)
if err := os.MkdirAll(dir, 0755); err != nil {
    return fmt.Errorf("failed to create directory: %w", err)
}
```

### 自动清理空目录

删除文件后，尝试删除父目录：

```go
dir := filepath.Dir(path)
if entries, err := os.ReadDir(dir); err == nil && len(entries) == 0 {
    os.Remove(dir)
}
```

## 使用示例

### 同步操作

```go
// 创建实际执行的分发器
dist := distributor.NewDistributor(false)

// 执行构建计划
if err := dist.ExecutePlan(plan); err != nil {
    log.Printf("Error executing plan: %v", err)
    return err
}

// 写入 manifest
manifestMgr.Write(plan, projectName, agent)
```

### 清理操作

```go
// 读取 manifest
mft, _ := manifestMgr.Read("backend", "codex")

// 反向删除（子文件先删）
for i := len(mft.Entries) - 1; i >= 0; i-- {
    entry := mft.Entries[i]
    if err := dist.CleanEntry(entry); err != nil {
        log.Printf("Warning: failed to delete %s: %v", entry.OutputPath, err)
    }
}
```

### Dry Run 模式

```go
// 创建 dry-run 分发器
dist := distributor.NewDistributor(true)

// 执行（只打印，不实际操作）
dist.ExecutePlan(plan)

// 输出示例：
// Would symlink: /repo/content/skill/auth.md -> /project/.codex/skills/auth.md
```

## 错误处理

| 错误情况 | 错误信息 | 处理方式 |
|----------|----------|----------|
| 无源文件 | `no source items specified` | 返回错误 |
| 创建目录失败 | `failed to create directory` | 返回错误 |
| 删除现有文件失败 | `failed to remove existing file` | 返回错误 |
| 创建 symlink 失败 | `failed to create symlink` | 返回错误 |
| 打开源文件失败 | `failed to open source` | 返回错误 |
| 创建目标文件失败 | `failed to create destination` | 返回错误 |
| 复制失败 | `failed to copy` | 返回错误 |

## 设计原则

1. **幂等性**：多次执行相同计划应该产生相同结果
2. **原子性**：单个文件操作失败不影响其他文件
3. **安全性**：不执行任何破坏性操作（除非明确指定）
4. **可预测**：dry-run 模式准确预测实际行为

## 注意事项

1. **权限问题**：确保有权限创建符号链接和目录
2. **跨平台**：Windows 对符号链接支持有限，可能需要管理员权限
3. **路径长度**：避免超长路径，某些文件系统有长度限制
4. **并发写入**：不支持并发写入同一文件
