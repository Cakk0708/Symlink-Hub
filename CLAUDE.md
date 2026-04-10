# Claude AI 协作指南

## ⚠️ 重要前提：任务执行前必须阅读项目地图

**在任何任务开始执行前，你必须先阅读 `.claude/docs/map.md` 文档，了解项目的模块结构和各模块的职责。**

### 执行流程

1. **任务接收** → 理解用户需求
2. **阅读地图** → 阅读 `.claude/docs/map.md`
3. **识别模块** → 确定任务涉及哪些模块
4. **阅读文档** → 阅读相关模块的详细文档
5. **开始开发** → 基于对模块的理解进行开发

**不要跳过地图阅读步骤！**

---

## 项目概述

Symlink-Hub 是一个本地 AI 配置内容中枢系统，用于统一管理 AI coding 工具的配置内容（agents、skills、rules、docs、commands），并根据规则自动分发到多个项目。

### 技术栈

- **语言**: Go 1.26+
- **配置**: YAML
- **内容**: Markdown + Frontmatter

### 项目结构

```
Symlink-Hub/
├── cmd/symlink-hub/     # CLI 入口
├── internal/            # 内部模块
│   ├── core/           # 核心类型
│   ├── config/         # 配置加载
│   ├── content/        # 内容扫描
│   ├── selector/       # 内容选择
│   ├── mapper/         # 路径映射
│   ├── planner/        # 计划生成
│   ├── manifest/       # 清单管理
│   └── distributor/    # 文件分发
├── fixtures/           # 示例数据
└── .claude/docs/       # 模块文档
    ├── map.md          # ← 模块地图（必读）
    ├── core.md
    ├── config.md
    ├── content.md
    ├── selector.md
    ├── mapper.md
    ├── planner.md
    ├── manifest.md
    └── distributor.md
```

---

## 开发指南

### 1. 理解模块职责

每个模块都有明确的单一职责：
- **core**: 数据类型定义
- **config**: 配置加载
- **content**: 内容扫描解析
- **selector**: 内容选择逻辑
- **mapper**: 路径映射
- **planner**: 计划生成
- **manifest**: 清单管理
- **distributor**: 文件操作

### 2. 遵循依赖关系

```
core (基础)
  ↓
config, content (数据源)
  ↓
selector, mapper (处理)
  ↓
planner (计划)
  ↓
manifest, distributor (执行)
```

### 3. 代码风格

- 使用清晰的命名
- 添加必要的注释
- 错误处理要明确
- 保持函数单一职责

### 4. 测试

修改代码后，运行以下命令测试：

```bash
go build -o symlink-hub cmd/symlink-hub/main.go
./symlink-hub doctor
./symlink-hub dry-run
./symlink-hub sync
./symlink-hub clean
```

---

## 常见任务

### 添加新的内容类型

1. 阅读 `core.md` 和 `mapper.md`
2. 在 `core/types.go` 添加 `ContentType`
3. 在 `mapper/mapper.go` 添加映射逻辑
4. 在配置文件中添加 root 定义

### 修改选择逻辑

1. 阅读 `selector.md`
2. 修改 `selector/selector.go`
3. 测试选择结果

### 添加新的分发模式

1. 阅读 `distributor.md`
2. 在 `core/types.go` 添加 `DistributionMode`
3. 在 `distributor/distributor.go` 实现逻辑

---

## 注意事项

1. **无外部依赖**: YAML 解析是手写的，不要引入依赖
2. **路径处理**: 统一使用绝对路径
3. **错误处理**: 明确的错误信息，便于调试
4. **向后兼容**: 修改配置格式时考虑兼容性

---

## 文档更新

当修改模块功能时，请同步更新对应的文档：
- 修改了数据结构 → 更新 `core.md`
- 修改了配置格式 → 更新 `config.md`
- 修改了模块逻辑 → 更新对应模块文档

保持文档与代码同步是团队协作的基础。
