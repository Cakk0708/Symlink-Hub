# Claude Code 项目配置

本目录包含 Claude Code 专用的配置文件和自定义命令。

## 目录结构

```
.claude/
├── .gitignore          # Git 忽略规则
├── README.md           # 本文件
└── commands/           # 自定义命令
    ├── apifox.md       # 生成 ApiFox JSON Schema
    └── code_define.md  # 变量命名建议
```

## 使用方法

### 自定义命令

在对话中直接引用命令，例如：

```
请帮我生成 /apifox POST apps/SMS/pmconfig/list DetailListSerializer
```

```
请帮我生成 /code_define 生产工单编号
```

### 命令说明

| 命令 | 功能 | 参数 |
|-----|------|------|
| /apifox | 生成 ApiFox 可导入的 JSON Schema | Method Path Serializers |
| /code_define | 输出适合 MOM 系统的变量命名建议 | 单词/短语 |

