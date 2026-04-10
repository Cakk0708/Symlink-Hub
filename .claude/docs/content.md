# Content Module

## 概述

`content` 模块负责扫描内容库目录，解析 Markdown 文件的 frontmatter 元数据，并验证内容项的完整性。

## 模块组成

### Scanner

内容扫描器，遍历内容库目录：

```go
scanner := content.NewScanner(cfg.ContentRoot)
items, err := scanner.Scan()
```

**Scan() 方法行为**：
1. 递归遍历 `ContentRoot` 目录
2. 查找所有 `.md` 文件（不区分大小写）
3. 对每个文件调用 `ParseContentFile()`
4. 解析失败的文件会输出警告但继续扫描
5. 返回所有成功解析的内容项

### Parser

Frontmatter 解析器，提取 Markdown 文件的元数据：

```go
item, err := content.ParseContentFile(filePath, contentRoot)
```

**支持的 Frontmatter 格式**：

```markdown
---
id: auth-login
title: Auth Login Skill
type: skill
targets:
  - codex
  - claude
tags:
  - backend
  - auth
projects:
  - backend
weight: 20
status: active
---

# Auth Login

内容正文...
```

**解析规则**：
- 必须以 `---` 开头
- Frontmatter 必须以 `---` 结束
- 支持 `-` 开头的数组项
- 支持 `key: value` 的键值对
- 值的引号会被自动去除

**必填字段验证**：
| 字段 | 说明 |
|------|------|
| `id` | 内容项唯一标识符 |
| `title` | 显示标题 |
| `type` | 内容类型（agent/skill/rule/doc/command） |

**可选字段**：
| 字段 | 说明 | 默认值 |
|------|------|--------|
| `targets` | 适用 agent 列表 | 所有 agent |
| `tags` | 标签列表 | 空 |
| `projects` | 适用项目列表 | 所有项目 |
| `weight` | 优先级权重 | 0 |
| `status` | 状态 | active |

**运行时注入字段**：
- `SourcePath`：源文件的绝对路径
- `Checksum`：内容的 CRC32 校验和
- `LastModified`：文件的最后修改时间（ISO 8601）

### Validator

内容项验证器：

```go
err := content.ValidateContentItems(items)
```

**验证项**：
1. **ID 唯一性**：检查是否有重复的 `id`
2. **类型有效性**：检查 `type` 是否为支持的类型
3. **路径存在性**：检查 `SourcePath` 对应的文件是否存在

**错误示例**：
```
duplicate id 'auth-login' in /path/to/a.md and /path/to/b.md
invalid type 'invalid-type' in /path/to/file.md
```

## 目录结构建议

内容库推荐结构：

```
content/
├── agent/           # Agent 主指令文件
│   ├── codex-base.md
│   └── claude-base.md
├── skill/           # Skill 内容
│   ├── auth-login.md
│   └── api-client.md
├── rule/            # Rule 内容
│   ├── commit-format.md
│   └── code-style.md
├── doc/             # 文档内容
│   └── api-reference.md
└── command/         # 命令内容
    └── deploy.md
```

## 使用示例

```go
// 创建扫描器
scanner := content.NewScanner("./fixtures/content")

// 扫描内容
items, err := scanner.Scan()
if err != nil {
    log.Fatal(err)
}

// 验证内容
if err := content.ValidateContentItems(items); err != nil {
    log.Fatal(err)
}

// 处理内容项
for _, item := range items {
    fmt.Printf("Found: %s (%s)\n", item.ID, item.Type)
}
```

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 文件读取失败 | 返回错误，终止扫描 |
| Frontmatter 解析失败 | 输出警告，继续扫描 |
| 验证失败 | 返回详细错误信息 |

## 性能考虑

- 扫描是 I/O 密集型操作，大内容库可能需要较长时间
- 校验和计算使用简单 CRC32，适合中小型内容库
- 如需处理超大型内容库，考虑添加并发扫描
