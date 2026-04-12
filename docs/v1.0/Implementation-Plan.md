# Symlink-Hub 实施计划 v1.0

## 1. 第一阶段要交付什么

第一阶段不追求完整产品，而是交付一个能在真实项目里使用的 CLI 最小闭环：

1. 从 `content/` 读取内容项。
2. 从 `symlink-hub.config.yaml` 读取项目与 agent 配置。
3. 运行 `dry-run` 输出 Build Plan。
4. 运行 `sync` 将内容分发到目标项目。
5. 运行 `clean` 清理已生成产物。
6. 运行 `import` 从目标项目反向导入已有配置到内容库。

### 当前 Python 实现

Python 原型已实现以下功能，可作为 TypeScript 版本的参考：

- `update_link.py`：完整的 sync 功能（读取 config → 生成符号链接 → 同步到目标项目）
- `import_project.py`：反向导入功能（扫描目标项目 → 导入文件到 data/ → 更新 config/tags）

## 2. 任务拆分

### 2.1 初始化工程

- 建立 `package.json`
- 建立 `tsconfig.json`
- 建立 `src/` 目录
- 配置 lint / test / build 脚本

### 2.2 先做纯核心

优先实现不依赖 CLI 的纯函数模块：

- content parser
- schema validator
- project selector
- path mapper
- build planner

这些模块稳定后，再接 CLI 和文件写入。

### 2.3 import 功能

- 项目目录扫描（skills、rules、agents、commands、docs、memory、mcp）
- 路径到资源类型的映射
- 已有资源检测（按 name 去重）
- 交互式标签选择
- 文件复制与 config/tags 自动更新

### 2.4 再接文件系统

- symlink writer
- copy writer
- manifest store
- clean executor

### 2.5 最后接命令入口

- `dry-run`
- `sync`
- `status`
- `doctor`
- `clean`

## 3. 建议的数据流分层

建议按下面分层开发，避免 CLI 逻辑和业务逻辑耦合：

```text
CLI Command
  -> Application Service
  -> Domain Planner / Selector
  -> Infrastructure FS / Manifest
```

对应建议：

- `cli/` 只负责参数解析和打印
- `core/` 负责编排 use case
- `domain/` 负责纯模型与规则
- `infrastructure` 职责暂时并入 `core/distribute` 与 `core/manifest`

## 4. 样例用例

### 4.1 导入已有项目

```bash
# 将目标项目中已有的 .claude/ 配置导入到内容库
python import_project.py --project duolingo_backend --scheme claude
```

流程：
1. 扫描 `duolingo_backend` 项目下的 `.claude/` 目录
2. 识别 skills、rules、agents 等资源
3. 对比 config.json 已有条目，筛选新资源
4. 交互式为每个资源选择标签
5. 复制文件到 `data/`，更新 config.json 和 tags.json

### 4.2 分发到目标项目

```bash
# 将内容库中的资源分发到目标项目
python update_link.py --scheme claude
```

### 4.3 fixtures 样例

建议在 `fixtures/` 下准备一组最小样例：

- `fixtures/content/agent/codex-base.md`
- `fixtures/content/skill/auth-login.md`
- `fixtures/content/rule/commit-format.md`
- `fixtures/projects/backend/`

这样可以直接做集成测试，也方便后续写 README 示例。

## 5. 验收标准

满足以下条件即可进入下一阶段：

1. `dry-run` 能稳定输出 create / replace / skip。
2. `sync` 后目标项目出现正确文件。
3. `clean` 只删除 manifest 管理的文件。
4. 重复 `id`、重复 agent 主文件、非法 frontmatter 会报错。
5. `doctor` 能识别至少三类问题：
   - 缺失源文件
   - 缺失目标文件
   - 目标文件与 manifest 不一致

## 6. 当前建议的下一步

仓库现在还没有代码，实现顺序建议直接是：

1. 初始化 TypeScript CLI 工程
2. 写 config/content schema
3. 写 planner 与 dry-run
4. 接 sync + manifest
5. 接 clean/status/doctor

这个顺序能最早暴露数据模型问题，减少后面返工。
