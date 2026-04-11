# APIFox 导入技能目录结构

```
apifox-import/
├── SKILL.md                    # [核心] 技能定义文件
├── README.md                   # 本文件
├── scripts/                    # 可执行脚本（预留）
│   └── parse_apifox.py        # APIFox JSON 解析脚本
├── references/                 # 参考文档
│   ├── bdm-example.json       # BDM 模块 APIFox 导出示例
│   └── field-mapping.md       # JSON Schema 到 Django 字段映射表
└── assets/                     # 代码模板
    ├── model-template.py      # Django 模型模板
    ├── serializer-template.py # 序列化器模板
    ├── viewset-template.py    # 视图集模板
    └── urls-template.py       # URL 配置模板
```

## 使用方法

当用户提供 APIFox JSON 文件时，Claude 将自动：

1. 解析 JSON 结构，提取接口和数据模型定义
2. 分析接口模式（CRUD、批量操作等）
3. 生成符合 PMS 项目规范的 Django 代码

## 触发关键词

- `apifox`
- `.apifox.json`
- "导入接口"
- "接口文档"
- "生成接口代码"

## 生成的代码结构

```
apps/<MODULE>/
├── models.py           # Django 模型
├── serializers.py      # DRF 序列化器
├── views.py            # 视图集
├── urls.py             # URL 配置
└── enums.py            # 枚举定义（如有）
```

## 特殊处理

1. **批量操作模式**：请求体使用 `models` 数组包装
2. **JWT 认证**：所有接口自动添加 `IsAuthenticated` 权限
3. **时间戳字段**：自动添加 `created_at` 和 `updated_at`
4. **软删除**：支持 `disable_flag` 字段的软删除模式
