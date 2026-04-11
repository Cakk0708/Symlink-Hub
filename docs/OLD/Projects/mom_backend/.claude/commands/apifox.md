---
description: 输出ApiFox可导入使用的JSON Schema代码（传参：Method Path Serializers）
---

请对 $2 文件 $3 序列化器整理一份用于导入 Apifox 数据模型的 JSON Schema，用于向该序列化器发送 $1 请求创建数据，输出 JSON Schema 内容包含字段名称、字段类型、中文名（title）、说明（description）、必填情况

$1 = 请求方式
$2 = 路径
$3 = 序列化器

请求方式：
GET: 分析输出项目路径下该序列化器发生 GET 方法后输出的字段
POST: 分析输出项目路径下该序列化器 Create方法 添加数据所需的所有字段

标准格式：
{
    "type": "object",
    "description": ...,
    "properties": {
        "category": {
            "type": ...,
            "title": ...,
            "description": ...,
            "enum": [
                ...
            ],
            "x-apifox-mock": ...
        },
        ...
    },
    "required": [
        ...
    ],
    "x-apifox-orders": [
        ...
    ]
}

请确保输出结果标准：
1. 输出 Apifox 导入可用的 JSON Schema 格式的结果 JSON
2. 仔细阅读模块 enums.py 输出正确的 mock 到结果 JSON
3. 仔细阅读模块 serializers.py 输出完整的字段内容到结果 JSON
4. 仔细阅读模块 models.py 输出正确的 title、description 到结果 JSON
5. 参考上述提供的标准格式
6. 若为 PrimaryKeyRelatedField 类型字段 mock 为@pick(1, 2, 3)

其他要求：
1. 请保证输出的 json 内容行请不要携带行序号，这将影响我复制结果
