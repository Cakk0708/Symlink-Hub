# Vue 接口函数模板参考

> 按需读取此文件。在生成"接口函数"章节时加载。

---

## LIST 接口模板

### `get{ModelName}List`

获取{ModelName}列表。

```typescript
get{ModelName}List(params: {ModelName}ListParams)
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | `number` | 否 | 页码，从 0 开始，默认 0 |
| page_size | `number` | 否 | 每页数量，默认 20 |
| {filter_field} | `string` | 否 | {说明} |

**返回示例**

```typescript
{
  msg: 'ok',
  data: {
    total: 100,
    page: 0,
    page_size: 20,
    items: {ModelName}[]
  }
}
```

**调用示例**

```typescript
const { data } = await get{ModelName}List({ page: 0, page_size: 20 })
```

---

## CREATE 接口模板

### `create{ModelName}`

创建{ModelName}。

```typescript
create{ModelName}(payload: {ModelName}Payload)
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| {field} | `string` | ✅ | {说明} |
| {field} | `string` | 否 | {说明} |

**返回示例**

```typescript
{
  msg: 'ok',
  data: {ModelName}
}
```

**调用示例**

```typescript
const { data } = await create{ModelName}({ {field}: '{value}' })
```

---

## RETRIEVE 接口模板

### `get{ModelName}Detail`

获取{ModelName}详情。

```typescript
get{ModelName}Detail(id: number)
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | `number` | ✅ | {ModelName} ID |

**返回示例**

```typescript
{
  msg: 'ok',
  data: {ModelName}
}
```

**调用示例**

```typescript
const { data } = await get{ModelName}Detail(1)
```

---

## UPDATE 接口模板

### `update{ModelName}`

更新{ModelName}。

```typescript
update{ModelName}(id: number, payload: Partial<{ModelName}Payload>)
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | `number` | ✅ | {ModelName} ID |
| {field} | `{type}` | 否 | {说明} |

**返回示例**

```typescript
{
  msg: 'ok',
  data: {ModelName}
}
```

**调用示例**

```typescript
const { data } = await update{ModelName}(1, { {field}: '{new_value}' })
```

---

## BULK DELETE 接口模板

### `delete{ModelName}Batch`

批量删除{ModelName}。

```typescript
delete{ModelName}Batch(ids: number[])
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | `number[]` | ✅ | 待删除的 ID 列表 |

**返回示例**

```typescript
{
  msg: 'ok',
  data: null
}
```

**调用示例**

```typescript
await delete{ModelName}Batch([1, 2, 3])
```

---

## 自定义 Action 接口模板

### `{actionName}`

{action 描述}。

```typescript
{actionName}(id: number, payload?: {ActionPayload})
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | `number` | ✅ | {ModelName} ID |
| {field} | `{type}` | 否 | {说明} |

**返回示例**

```typescript
{
  msg: 'ok',
  data: {说明返回结构}
}
```

**调用示例**

```typescript
const { data } = await {actionName}(1, { {field}: '{value}' })
```

---

## 文件上传接口模板

### `upload{ModelName}File`

上传文件。

```typescript
upload{ModelName}File(id: number, file: File, onProgress?: (percent: number) => void)
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | `number` | ✅ | 关联对象 ID |
| file | `File` | ✅ | 文件对象 |
| onProgress | `function` | 否 | 上传进度回调 |

**调用示例**

```typescript
await upload{ModelName}File(1, file, (percent) => {
  console.log(`上传进度：${percent}%`)
})
```