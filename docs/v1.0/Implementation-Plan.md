# Symlink-Hub 实施计划 v1.0

## 1. 第一阶段要交付什么

第一阶段不追求完整产品，而是交付一个能在真实项目里使用的 CLI 最小闭环：

1. 从 `content/` 读取内容项。
2. 从 `symlink-hub.config.yaml` 读取项目与 agent 配置。
3. 运行 `dry-run` 输出 Build Plan。
4. 运行 `sync` 将内容分发到目标项目。
5. 运行 `clean` 清理已生成产物。

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

### 2.3 再接文件系统

- symlink writer
- copy writer
- manifest store
- clean executor

### 2.4 最后接命令入口

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
