# Symlink-Hub

AI Coding 配置中枢与内容编排系统。统一管理 skills、rules、agents 等内容，根据标签自动构建并分发到多个目标项目。

## 核心理念

- **Single Source of Truth** — 所有内容只在 `data/` 维护一份，目标项目只消费
- **Tag-driven** — 通过标签匹配决定内容分发到哪些项目
- **构建产物** — 目标项目中的文件是构建结果，不是源文件

## 数据目录结构

```text
data/
├── config.json       # 资源元信息（name, tags, structure 等）
├── project.json      # 目标项目定义（key, tags, path）
├── tags.json         # 可用标签列表
├── skills/           # 技能文件
├── rules/            # 规则文件
├── agents/           # Agent 指令
├── commands/         # 命令文件
├── docs/             # 文档文件
├── memory/           # Memory 文件
├── mcp/              # MCP 配置
├── references/       # 技能引用文件
└── others/           # 其他文件
```

## 使用方式

### 生成链接：update_link.py

根据 `data/` 中的配置，在 `.links/` 下生成项目符号链接，并同步到目标项目路径。

```bash
# 交互式选择方案
python update_link.py

# 指定方案
python update_link.py --scheme claude

# 仅生成指定项目
python update_link.py --scheme claude --project duolingo_backend
```

**支持的方案：**

| 方案 | 工作目录 | Memory 文件 |
| --- | --- | --- |
| claude | `.claude/` | `CLAUDE.md` |
| codex | `.codex/` | `AGENTS.md` |

### 导入项目资源：import_project.py

扫描目标项目中已有的 AI 配置文件，反向导入到 `data/` 目录。适用于项目初始化时，将现有配置迁移到统一管理。

```bash
# 导入指定项目
python import_project.py --project duolingo_backend --scheme claude

# 交互式选择方案
python import_project.py --project duolingo_backend
```

**导入流程：**

1. 扫描目标项目的 `.claude/` 或 `.codex/` 目录
2. 识别 skills、rules、agents、commands、docs、memory、mcp 等资源
3. 跳过 config.json 中已存在的同名资源
4. 交互式为每个新资源选择标签
5. 复制文件到 `data/` 并更新 `config.json`、`tags.json`

**扫描的目录结构（以 claude 为例）：**

```text
project_path/
├── CLAUDE.md                    → memory
├── .mcp.json                    → mcp
└── .claude/
    ├── skills/
    │   └── skill-name/
    │       ├── SKILL.md         → skill
    │       └── references/
    │           └── ref.md       → reference
    ├── rules/
    │   └── serializers/
    │       └── rule.md          → rule (structure: ["serializers"])
    ├── agents/
    │   └── agent.md             → agent
    ├── commands/
    │   └── cmd.md               → command
    └── docs/
        └── doc.md               → doc
```

## 配置文件说明

### project.json

定义目标项目，每个项目包含标签和绝对路径。

```json
{
    "duolingo_backend": {
        "tags": ["duolingo_backend", "python-backend"],
        "path": "/Users/cakk/Project/Duolingo/backend"
    }
}
```

### config.json

定义每个资源的元信息，按资源类型分组。资源 ID 为 20 位随机字符串。

```json
{
    "rules": [
        {
            "TUltQoLbiugO7kjYrPDF": {
                "name": "delete-serializer",
                "tags": ["python-backend"],
                "structure": ["serializers"],
                "description": "规范删除序列化器必须使用可校验的批量 ids 字段。"
            }
        }
    ],
    "skills": [
        {
            "wyGb01LmWc2gMQUrZ8Ef": {
                "name": "git-commit",
                "tags": ["global"],
                "reference": ["oA16ZsPltcnkgR4iaLQw"]
            }
        }
    ]
}
```

### tags.json

所有可用标签的列表。

```json
["root", "global", "duolingo", "python-backend"]
```

## 典型工作流

```bash
# 1. 初始化新项目：导入现有配置到 data/
python import_project.py --project new_project --scheme claude

# 2. 生成链接：将 data/ 内容分发到目标项目
python update_link.py --scheme claude

# 3. 修改 data/ 中的内容后重新生成
python update_link.py --scheme claude --project new_project
```
