# PM - DeliverableFile 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `DeliverableFile`
> Base URL: `/api/pm/deliverable`

---

## 认证说明

所有接口均需在请求头中携带 JWT Token：

```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 接口列表

| 方法 | 路径 | 描述 | 需要认证 |
|------|------|------|----------|
| POST | `/file/upload` | 上传交付物文件 | ✅ |
| POST | `/file/template` | 基于模板创建交付物文件 | ✅ |

---

## 接口详情

### 1. 上传交付物文件

**接口地址：** `POST /api/pm/deliverable/file/upload`

**功能描述：** 上传交付物文件到临时目录，支持飞书和阿里云 OSS 两种存储方式

**请求头：**

```
Content-Type: multipart/form-data
Authorization: Bearer YOUR_JWT_TOKEN
```

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | ✅ | 上传的文件 |
| storage_provider | String | ❌ | 存储服务商，可选值：`feishu`(默认)、`aliyun_oss` |

**请求示例：**

```bash
curl -X POST "http://your-domain.com/api/pm/deliverable/file/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/your/file.pdf" \
  -F "storage_provider=feishu"
```

**成功响应：**

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "insertId": 123
  }
}
```

**响应字段说明：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | Integer | 状态码，0 表示成功 |
| msg | String | 响应消息 |
| data.insertId | Integer | 新创建的文件 ID |

**错误响应：**

```json
{
  "code": 1,
  "msg": "请选择要上传的文件"
}
```

```json
{
  "code": 1,
  "msg": "文件名称不能长于100字符"
}
```

**业务说明：**

- 上传的文件首先保存到临时目录
- 创建 `DeliverableFile` 记录，标记为临时状态（`is_temp=True`）
- 返回的 `insertId` 用于后续关联到交付物实例

---

### 2. 基于模板创建交付物文件

**接口地址：** `POST /api/pm/deliverable/file/template`

**功能描述：** 基于飞书模板创建交付物文件，自动处理目录结构和文件复制

**请求头：**

```
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN
```

**请求参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| nodeId | Integer | ✅ | 节点 ID |
| deliverableDefinitionVersionId | Integer | ✅ | 交付物定义版本 ID |

**请求示例：**

```json
{
  "nodeId": 456,
  "deliverableDefinitionVersionId": 789
}
```

**cURL 示例：**

```bash
curl -X POST "http://your-domain.com/api/pm/deliverable/file/template" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "nodeId": 456,
    "deliverableDefinitionVersionId": 789
  }'
```

**成功响应：**

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "insertId": 124
  }
}
```

**错误响应：**

```json
{
  "code": 1,
  "msg": "该交付物定义未配置模板"
}
```

```json
{
  "code": 1,
  "msg": "模板未配置飞书信息"
}
```

```json
{
  "code": 1,
  "msg": "项目文件夹创建失败"
}
```

```json
{
  "code": 1,
  "msg": "复制模板文件失败"
}
```

**业务流程：**

1. 检查交付物定义版本是否配置了模板
2. 检查并创建目录结构（客户编码目录、机型编码目录、交付物目录）
3. 调用飞书文件管理器复制模板文件
4. 设置文件权限：组织内获得链接的人可阅读（`link_share_entity: tenant_readable`）
5. 创建 `DeliverableFile` 和 `DeliverableFileFeishu` 记录
6. 返回新创建的文件 ID

---

## 数据模型

### DeliverableFile（交付物文件主表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BigAutoField | 文件 ID |
| name | CharField(255) | 文件名称 |
| size | CharField(255) | 文件大小（格式化后，如 "1.5 MB"） |
| category | CharField(255) | 文件类型：`file`、`sheet`、`doc`、`docx`、`pdf`、`image`、`url`、`folder` |
| storage_provider | CharField(50) | 存储服务商：`FEISHU`（默认）、`ALIYUN_OSS` |
| temp_path | CharField(500) | 临时文件路径 |
| temp_token | CharField(255) | 临时访问令牌 |
| is_temp | BooleanField | 是否为临时文件 |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

### DeliverableFileFeishu（飞书存储子表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | AutoField | 记录 ID |
| file | OneToOneField | 关联的 DeliverableFile |
| token | CharField(255) | 飞书文件 token |

---

## 存储服务商枚举

| 值 | 显示名称 | 说明 |
|----|----------|------|
| FEISHU | 飞书云文档 | 默认存储方式 |
| ALIYUN_OSS | 阿里云 OSS | 阿里云对象存储 |

---

## 文件类型枚举

| 值 | 显示名称 |
|----|----------|
| file | 通用文件 |
| sheet | 飞书表格 |
| doc | 飞书文档 |
| docx | Word文档 |
| pdf | PDF文档 |
| image | 图片 |
| url | 外部链接 |
| folder | 文件夹 |

---

## 错误响应

所有接口错误时统一返回：

```json
{
  "code": 1,
  "msg": "错误描述信息"
}
```

**常见错误场景**

| 场景 | 错误信息 |
|------|----------|
| 未选择文件 | 请选择要上传的文件 |
| 文件名过长 | 文件名称不能长于100字符 |
| 未配置模板 | 该交付物定义未配置模板 |
| 模板无飞书信息 | 模板未配置飞书信息 |
| 文件夹创建失败 | 项目文件夹创建失败 |
| 文件复制失败 | 复制模板文件失败 |
| 未认证 | 401 Unauthorized |
| 无权限 | 403 Forbidden |

---

## 完整 cURL 示例

```bash
# 1. 上传文件到飞书
curl -X POST "http://your-domain.com/api/pm/deliverable/file/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "storage_provider=feishu"

# 2. 上传文件到阿里云 OSS
curl -X POST "http://your-domain.com/api/pm/deliverable/file/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "storage_provider=aliyun_oss"

# 3. 基于模板创建文件
curl -X POST "http://your-domain.com/api/pm/deliverable/file/template" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "nodeId": 456,
    "deliverableDefinitionVersionId": 789
  }'
```
