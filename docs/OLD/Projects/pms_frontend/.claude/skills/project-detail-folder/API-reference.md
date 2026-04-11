# PMS 文件管理模块 - API 接口文档

## 接口列表

### 1. 获取项目文件夹结构

**接口地址**: `GET /pm/project/{project_id}/folder`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | number | 是 | 项目 ID |

**响应示例**:
```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 3,
        "name": "DELIV0002",
        "deliverables": [
          {
            "id": 3,
            "name": "1.pdf",
            "version": null,
            "fileCategory": "document",
            "state": "INITIAL_FROZEN",
            "createdAt": "2026-03-10 18:35:00",
            "createdBy": {
              "id": 1,
              "nickname": "范凯强",
              "avatar": "https://s3-imfile.feishucdn.com/static-resource/v1/v2_707d25b0-e918-45c3-8fdb-490093874f4g~?image_size=72x72&cut_type=&quality=&format=image&sticker_format=.webp"
            }
          }
        ]
      }
    ],
    "count": 1
  }
}
```

**前端调用**:
```javascript
const res = await this.$util.request({
  url: `pm/project/${this.projectId}/folder`,
  method: 'GET'
})
```

---

### 2. 上传交付物文件

**接口地址**: `POST /pm/project/{project_id}/deliverable`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | number | 是 | 项目 ID |
| folder_id | number | 是 | 文件夹 ID |
| file | File | 是 | 文件对象 |
| file_category | string | 是 | 文件类别 (document/image/video/url) |

**请求示例**:
```javascript
const formData = new FormData()
formData.append('file', fileObject)
formData.append('folder_id', folderId)
formData.append('file_category', 'document')

const res = await this.$util.request({
  url: `pm/project/${projectId}/deliverable`,
  method: 'POST',
  data: formData,
  header: {
    'Content-Type': 'multipart/form-data'
  }
})
```

**响应示例**:
```json
{
  "msg": "success",
  "data": {
    "id": 4,
    "name": "uploaded.pdf",
    "fileCategory": "document",
    "state": "INITIAL",
    "createdAt": "2026-03-10 19:00:00",
    "createdBy": {
      "id": 1,
      "nickname": "范凯强",
      "avatar": "https://..."
    }
  }
}
```

---

### 3. 删除交付物文件

**接口地址**: `DELETE /pm/deliverable/{deliverable_id}`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| deliverable_id | number | 是 | 交付物 ID |

**响应示例**:
```json
{
  "msg": "success",
  "data": {
    "id": 3,
    "deleted": true
  }
}
```

**前端调用**:
```javascript
const res = await this.$util.request({
  url: `pm/deliverable/${deliverableId}`,
  method: 'DELETE'
})
```

---

### 4. 修改文件状态（冻结/解冻）

**接口地址**: `PATCH /pm/deliverable/{deliverable_id}/state`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| deliverable_id | number | 是 | 交付物 ID |
| state | number | 是 | 目标状态 (1=正常, 2=冻结) |
| reason | string | 否 | 冻结原因 |

**请求示例**:
```javascript
const res = await this.$util.request({
  url: `pm/deliverable/${deliverableId}/state`,
  method: 'PATCH',
  data: {
    state: 2,
    reason: '文件需要修改'
  }
})
```

**响应示例**:
```json
{
  "msg": "success",
  "data": {
    "id": 3,
    "state": "FROZEN"
  }
}
```

---

### 5. 获取文件预览链接（待实现）

**接口地址**: `GET /pm/deliverable/{deliverable_id}/preview`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| deliverable_id | number | 是 | 交付物 ID |

**响应示例**:
```json
{
  "msg": "success",
  "data": {
    "url": "https://open.feishu.cn/open/doc/...",
    "expire_time": "2026-03-10 20:00:00"
  }
}
```

**前端调用**:
```javascript
const res = await this.$util.request({
  url: `pm/deliverable/${deliverableId}/preview`,
  method: 'GET'
})

if (res.statusCode === 200) {
  const previewUrl = res.data.data.url
  window.open(`https://applink.feishu.cn/client/web_url/open?mode=window&height=700&width=900&url=${previewUrl}`)
}
```

---

### 6. 上传链接类型交付物（待实现）

**接口地址**: `POST /pm/project/{project_id}/deliverable/url`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | number | 是 | 项目 ID |
| folder_id | number | 是 | 文件夹 ID |
| url | string | 是 | 链接地址 |
| name | string | 是 | 显示名称 |

**请求示例**:
```javascript
const res = await this.$util.request({
  url: `pm/project/${projectId}/deliverable/url`,
  method: 'POST',
  data: {
    folder_id: folderId,
    url: 'https://example.com/document',
    name: '文档链接'
  }
})
```

---

## 错误码说明

### HTTP 状态码

| 状态码 | 说明 | 处理方式 |
|--------|------|----------|
| 200 | 成功 | 正常处理响应数据 |
| 400 | 请求参数错误 | 提示用户检查输入 |
| 401 | 未授权 | 触发 Token 刷新 |
| 403 | 无权限 | 提示用户无操作权限 |
| 404 | 资源不存在 | 提示用户资源已删除 |
| 500 | 服务器错误 | 提示用户稍后重试 |

### 业务错误码

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| 1001 | 项目不存在 | 提示项目已删除 |
| 1002 | 文件夹不存在 | 提示文件夹已删除 |
| 1003 | 文件不存在 | 提示文件已删除 |
| 2001 | 文件类型不支持 | 提示支持的文件类型 |
| 2002 | 文件大小超限 | 提示最大文件大小 |
| 2003 | 文件名重复 | 询问是否覆盖 |
| 3001 | 无上传权限 | 提示联系管理员 |
| 3002 | 无删除权限 | 提示联系管理员 |
| 3003 | 无修改权限 | 提示联系管理员 |

---

## 前端请求封装

### 统一请求方法

```javascript
// delivery-flie.vue
async getFolderData() {
  try {
    this.loading = true
    const res = await this.$util.request({
      url: `pm/project/${this.projectId}/folder`,
      method: 'GET'
    })

    if (res.statusCode === 200 && res.data.msg === 'success') {
      this.folderData = this.transformToTreeStructure(res.data.data.items || [])
      this.recursion(this.folderData)
      this.openCatalogue(this.lookUpList)
    } else {
      throw new Error(res.data.msg || '获取文件列表失败')
    }
  } catch (error) {
    uni.showToast({
      title: error.message || '网络错误',
      icon: 'none'
    })
    console.error('getFolderData error:', error)
  } finally {
    this.loading = false
  }
}
```

### 文件上传封装

```javascript
async uploadFile(file, folderId) {
  try {
    uni.showLoading({ title: '上传中...' })

    const res = await this.$util.uploadFile({
      url: `${this.$Global.config.path}pm/project/${this.projectId}/deliverable`,
      filePath: file.path,
      name: 'file',
      formData: {
        folder_id: folderId,
        file_category: this.getFileCategory(file.name)
      }
    })

    if (res.statusCode === 200) {
      const data = JSON.parse(res.data)
      if (data.msg === 'success') {
        uni.showToast({ title: '上传成功', icon: 'success' })
        return data.data
      }
    }

    throw new Error('上传失败')
  } catch (error) {
    uni.showToast({
      title: error.message || '上传失败',
      icon: 'none'
    })
    throw error
  } finally {
    uni.hideLoading()
  }
}
```

### 权限检查

```javascript
// 检查文件操作权限
checkFilePermission(action) {
  // 使用项目级权限
  return this.permission(1300, 'project') // 假设 1300 是文件管理权限
}

// 使用示例
async handleDelete(item) {
  if (!this.checkFilePermission('delete')) {
    uni.showToast({
      title: '无删除权限',
      icon: 'none'
    })
    return
  }

  // 执行删除操作
  await this.deleteFile(item.id)
}
```

---

## 接口版本管理

### 当前版本: v1.0.0

**变更记录**:
- ✅ 获取文件夹列表接口已更新
- ✅ 数据结构从树形改为平铺
- ✅ 添加 `createdBy.avatar` 字段
- ✅ 状态使用字符串枚举

### 已废弃接口

#### 旧版文件夹列表接口
```
POST project/at?type=10303
```

**废弃原因**: 数据结构不符合新的文件管理需求

**迁移指南**:
```javascript
// 旧接口
const res = await this.$util.request({
  url: 'project/at?type=10303',
  method: 'POST',
  data: { project_id: this.projectId }
})

// 新接口
const res = await this.$util.request({
  url: `pm/project/${this.projectId}/folder`,
  method: 'GET'
})
```
