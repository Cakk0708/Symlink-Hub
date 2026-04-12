# Symlink-Hub 系统设计 v1.0

## 1. 设计目标

基于 [PRD](/Users/cakk/Project/Symlink-Hub/docs/v1.0/PRD.md)，首期版本聚焦一个可靠的本地 CLI 工具，完成以下闭环：

1. 读取内容库中的 Markdown 内容及 frontmatter。
2. 读取项目配置，解析每个项目对 agent、tags、type 的消费规则。
3. 生成可审查的 Build Plan。
4. 以 `symlink` / `copy` 两种模式分发到目标项目。
5. 记录 manifest，支持 `status`、`doctor`、`clean`。

不在 v1.0 首期范围内的能力：

- GUI Editor
- merge 型冲突处理
- overlay / mirror 的完整高级语义
- 远程同步 / 团队协作服务端
- 实时文件监听

## 2. 产品边界

Symlink-Hub 的职责不是编辑目标项目中的 AI 配置，而是：

- 管理源内容
- 解析规则
- 构建目标文件树
- 负责分发与回收

因此目标项目中的文件应视为构建产物。用户可以手工修改，但系统会在 `doctor` 和后续 `sync` 中将其视为漂移状态。

## 3. 技术选型

首期建议使用 Node.js + TypeScript：

- 天然适合构建跨平台 CLI。
- 对 Markdown、frontmatter、文件系统操作生态成熟。
- 后续扩展 TUI、watch mode、插件机制成本较低。

建议依赖：

- `commander`：CLI 路由
- `gray-matter`：frontmatter 解析
- `zod`：配置与内容元数据校验
- `fast-glob`：内容扫描
- `fs-extra`：文件系统操作
- `yaml`：配置文件读写
- `picocolors`：终端输出

## 4. 仓库结构

建议仓库初始化为：

```text
Symlink-Hub/
├─ src/
│  ├─ cli/
│  │  ├─ index.ts
│  │  └─ commands/
│  │     ├─ sync.ts
│  │     ├─ dry-run.ts
│  │     ├─ clean.ts
│  │     ├─ status.ts
│  │     └─ doctor.ts
│  ├─ core/
│  │  ├─ content/
│  │  │  ├─ scanner.ts
│  │  │  ├─ parser.ts
│  │  │  └─ validators.ts
│  │  ├─ project/
│  │  │  ├─ loader.ts
│  │  │  └─ selectors.ts
│  │  ├─ build/
│  │  │  ├─ planner.ts
│  │  │  ├─ path-mapper.ts
│  │  │  ├─ aggregators.ts
│  │  │  └─ diff.ts
│  │  ├─ distribute/
│  │  │  ├─ writer.ts
│  │  │  ├─ symlink.ts
│  │  │  ├─ copy.ts
│  │  │  └─ clean.ts
│  │  ├─ manifest/
│  │  │  ├─ store.ts
│  │  │  └─ types.ts
│  │  └─ doctor/
│  │     └─ checks.ts
│  ├─ domain/
│  │  ├─ content-item.ts
│  │  ├─ project.ts
│  │  ├─ build-plan.ts
│  │  └─ manifest.ts
│  ├─ config/
│  │  ├─ app-config.ts
│  │  └─ constants.ts
│  └─ utils/
│     ├─ hash.ts
│     ├─ logger.ts
│     └─ paths.ts
├─ fixtures/
│  ├─ content/
│  └─ projects/
├─ docs/
│  └─ v1.0/
├─ package.json
├─ tsconfig.json
└─ README.md
```

## 5. 配置模型

首期建议采用一个仓库级配置文件：`symlink-hub.config.yaml`。

示例：

```yaml
contentRoot: ./content
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
  claude:
    agentFileName: CLAUDE.md
    roots:
      skill: .claude/skills
      rule: .claude/rules
      doc: .claude/docs
      command: .claude/commands

projects:
  - name: backend
    path: /Users/xxx/backend
    agents: [codex]
    includeTags: [global, backend, auth]
    excludeTags: [experimental]
    features: [backend]
    mode: symlink
    conflict: replace
```

设计原则：

- agent 的输出规则应由配置声明，不应硬编码在业务逻辑里。
- `projects` 是消费方定义，内容项不直接决定具体路径，只声明适用范围。
- `stateRoot` 用于存放 manifest、缓存和锁文件。

## 6. 内容模型

内容文件统一采用 Markdown + frontmatter。

示例：

```md
---
id: auth-login
title: Auth Login Skill
type: skill
targets:
  - codex
  - claude
tags:
  - global
  - backend
  - auth
projects:
  - backend
weight: 20
status: active
---

# Auth Login

...
```

### 6.1 字段约束

必填字段：

- `id`
- `title`
- `type`

可选字段：

- `targets`
- `tags`
- `projects`
- `weight`
- `status`

建议的 `type` 枚举：

- `agent`
- `skill`
- `rule`
- `doc`
- `command`

建议的系统字段：

- `sourcePath`：运行时注入，不写入源文件
- `checksum`：运行时生成
- `lastModified`：运行时生成

## 7. 项目选择逻辑

构建一个项目时，内容是否被纳入 Build Plan，按以下顺序判断：

1. `type` 是否被当前 agent 支持。
2. `targets` 为空时默认全 agent 可用，否则必须包含当前 agent。
3. `projects` 为空时默认全项目可用，否则必须包含当前项目名。
4. 内容 `tags` 必须至少命中项目 `includeTags` 之一。
5. 内容 `tags` 不能命中项目 `excludeTags`。
6. 若存在 `status` 且不为 `active`，则跳过。

说明：

- `includeTags` 为空时，表示不过滤标签。
- `agent` 类型允许唯一输出；同一项目同一 agent 若匹配多个 `agent` 内容项，应判定为冲突。
- `skill` / `rule` / `doc` / `command` 默认按单文件映射。

## 8. 输出映射规则

### 8.1 默认映射

| Type | 输出 |
| --- | --- |
| `agent` | `<projectRoot>/<agentFileName>` |
| `skill` | `<projectRoot>/<agentRoots.skill>/<id>.md` |
| `rule` | `<projectRoot>/<agentRoots.rule>/<id>.md` |
| `doc` | `<projectRoot>/<agentRoots.doc>/<id>.md` |
| `command` | `<projectRoot>/<agentRoots.command>/<id>.md` |

### 8.2 聚合能力

v1.0 设计保留聚合接口，但首期只实现 `agent` 聚合或单文件输出：

- `agent` 可由单个内容项直接生成
- 后续可扩展为多个片段聚合成一个 `CODEX.md`

因此 `aggregators.ts` 应保留统一接口：

```ts
interface Aggregator {
  supports(type: ContentType): boolean;
  aggregate(items: ContentItem[], context: BuildContext): AggregatedOutput[];
}
```

## 9. Build Plan 模型

```ts
type BuildAction = "create" | "replace" | "skip" | "conflict" | "delete";

interface BuildPlanEntry {
  action: BuildAction;
  projectName: string;
  agent: string;
  sourceItems: string[];
  outputPath: string;
  mode: "symlink" | "copy";
  reason?: string;
}

interface BuildPlan {
  generatedAt: string;
  entries: BuildPlanEntry[];
}
```

计划器输出必须是纯描述性的，不执行文件操作。这样 `dry-run` 与 `sync` 可共用同一条主链路。

## 10. 分发策略

### 10.1 `symlink`

适用于日常开发场景：

- 构建产物直接链接到源文件
- 更新内容库后目标项目即时生效
- 对聚合文件不适用，聚合文件必须走 `copy`

### 10.2 `copy`

适用于：

- 目标工具不接受软链接
- 目标文件需要冻结快照
- 目标文件是聚合产物

### 10.3 冲突策略

首期实现：

- `skip`
- `replace`
- `backup`

策略定义：

- `skip`：保留目标文件，不写入
- `replace`：直接覆盖或重建链接
- `backup`：移动为 `<file>.bak.<timestamp>` 后再写入

## 11. Manifest 设计

manifest 保存在：

```text
.symlink-hub/manifests/<projectName>.<agent>.json
```

示例：

```json
{
  "projectName": "backend",
  "agent": "codex",
  "generatedAt": "2026-04-10T10:00:00.000Z",
  "mode": "symlink",
  "entries": [
    {
      "sourceItemIds": ["auth-login"],
      "sourcePath": "/repo/content/skills/auth-login.md",
      "outputPath": "/Users/xxx/backend/.codex/skills/auth-login.md",
      "action": "create",
      "checksum": "sha256:xxxx"
    }
  ]
}
```

manifest 用途：

- `status`：展示上次同步结果
- `doctor`：检测目标文件是否被篡改、删除、失联
- `clean`：精确删除由系统创建的产物

## 12. 核心命令设计

### 12.1 `import`

```bash
symlink-hub import backend --agent claude
symlink-hub import backend --agent codex
```

行为：

- 加载项目配置，定位目标项目路径
- 扫描目标项目的工作目录（`.claude/` 或 `.codex/`）及根目录特殊文件
- 按路径规则将文件分类为对应资源类型
- 对比 config.json 中已有条目，跳过同名资源
- 交互式为新资源选择标签
- 复制文件到 `data/{type}/` 目录，生成随机 ID
- 更新 `config.json` 和 `tags.json`

扫描规则（以 claude 为例）：

| 路径模式 | 资源类型 | 说明 |
| --- | --- | --- |
| `.claude/skills/*/SKILL.md` | skills | skill 目录名为 name |
| `.claude/skills/*/references/*` | references | 自动关联到对应 skill |
| `.claude/rules/**/*.md` | rules | 子目录映射为 structure |
| `.claude/agents/**/*.md` | agents | 同上 |
| `.claude/commands/**/*.md` | commands | 同上 |
| `.claude/docs/**/*.md` | docs | 同上 |
| `CLAUDE.md` | memory | 根目录 |
| `.mcp.json` | mcp | 根目录 |

冲突策略：

- 同名资源（config 中已有相同 name）默认跳过
- 资源 ID 确保不与已有文件冲突

### 12.2 `sync`

```bash
symlink-hub sync backend --agent codex
symlink-hub sync all --agent codex
symlink-hub sync backend --agent codex --mode copy --conflict backup
```

行为：

- 加载配置
- 扫描内容
- 选择内容
- 生成 Build Plan
- 打印摘要
- 执行分发
- 写入 manifest

### 12.3 `dry-run`

```bash
symlink-hub dry-run
symlink-hub dry-run backend --agent claude
```

行为：

- 生成 Build Plan
- 不写文件
- 输出冲突和变更摘要

### 12.4 `clean`

```bash
symlink-hub clean backend --agent codex
```

行为：

- 读取 manifest
- 删除当前 agent 管理的构建产物
- 清理空目录

### 12.5 `status`

展示：

- 上次同步时间
- 条目数量
- 当前模式
- 漂移文件数量

### 12.6 `doctor`

检查项：

- 配置是否合法
- 内容 frontmatter 是否缺字段
- 是否存在重复 `id`
- 项目路径是否存在
- 目标 agent 输出规则是否完整
- manifest 与实际文件是否一致

## 13. 执行流程

```text
Load Config
  -> Scan Content Files
  -> Parse Frontmatter
  -> Validate Content Items
  -> Select Project + Agent
  -> Build Output Mapping
  -> Detect Conflicts
  -> Generate Build Plan
  -> Execute Distribution
  -> Write Manifest
```

关键原则：

- 校验失败应阻断写入
- 构建与分发解耦
- 每个阶段尽量输出结构化对象，便于测试

## 14. 错误模型

建议定义统一错误类型：

- `ConfigError`
- `ContentValidationError`
- `BuildConflictError`
- `DistributionError`
- `ManifestError`

CLI 层负责将错误格式化成人类可读输出，并返回非 0 exit code。

## 15. 测试策略

首期至少覆盖：

1. frontmatter 解析与 schema 校验
2. tag / target / project 选择逻辑
3. type 到路径的映射
4. Build Plan 冲突检测
5. symlink / copy 分发
6. manifest 生成与 clean 回收

建议测试分层：

- 单元测试：核心选择器、path mapper、planner
- 集成测试：基于临时目录运行 `sync -> status -> clean`

## 16. 开发里程碑

### M1: 可用骨架

- 初始化 TypeScript CLI
- 定义配置 schema
- 定义内容 schema
- 实现 `dry-run`

### M2: 完成同步闭环

- 实现 `sync`
- 支持 `symlink` / `copy`
- 写 manifest

### M3: 运维能力

- 实现 `status`
- 实现 `doctor`
- 实现 `clean`

### M4: 体验增强

- 更好的终端输出
- 示例内容库
- 示例项目模板

## 17. 首期实现建议

为了尽快验证价值，建议先收敛到以下约束：

- 只支持本地文件系统
- 只支持 `codex` 与 `claude`
- 只支持 Markdown 内容
- 只支持单仓库配置文件
- 只支持 `symlink` 和 `copy`
- `agent` 类型每个项目每个 agent 最多一个

这能确保 v1.0 先把“统一管理 + 自动分发”做扎实，再扩展更复杂的聚合、编辑器和团队能力。
