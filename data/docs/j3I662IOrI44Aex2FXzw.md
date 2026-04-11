# SM - 用户管理模块说明

## 模块定位

- **路径**: `/sm/user`
- **别名**: 用户管理
- **所属**: SM (系统管理) 模块
- **父模块**: [SM 模块](sm.md)

## 功能概述

用户管理模块负责系统用户的全生命周期管理，包括用户列表展示、新增用户、查看用户信息等功能。是系统权限管理的基础模块。

## 核心功能

### 1. 用户列表
- **列表展示**: 表格形式展示所有用户
- **分页功能**: 支持大量数据的分页加载
- **搜索功能**: 按用户名、真实姓名搜索
- **排序功能**: 支持按创建时间排序

### 2. 新增用户
- **表单验证**: 实时表单验证
- **提交功能**: 创建新用户
- **成功反馈**: 友好的成功提示
- **自动刷新**: 新增后自动刷新列表

### 3. 用户信息展示
- **基本信息**: 用户名、真实姓名、所属组织
- **创建时间**: 用户创建时间
- **状态信息**: 用户状态（启用/禁用）

## 数据字段

### 用户信息结构
```javascript
{
  id: Number,           // 用户ID
  username: String,     // 用户名
  real_name: String,    // 真实姓名
  organization: String, // 所属组织
  created_at: String,   // 创建时间
  status: String,       // 用户状态
  email: String,        // 邮箱（预留）
  phone: String,       // 手机号（预留）
  last_login: String    // 最后登录时间（预留）
}
```

## 技术实现

### 组件结构
```vue
<template>
  <div class="user-management">
    <!-- 搜索栏 -->
    <el-card>
      <el-form inline>
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="searchForm.real_name" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作按钮 -->
    <el-card>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增用户
      </el-button>
    </el-card>

    <!-- 用户列表 -->
    <el-card>
      <el-table :data="userList" v-loading="loading">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="real_name" label="真实姓名" />
        <el-table-column prop="organization" label="所属组织" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        @change="handlePageChange"
      />
    </el-card>
  </div>
</template>
```

### 接口调用
```javascript
// 获取用户列表
const fetchUsers = async () => {
  try {
    loading.value = true
    const response = await request.get('/SM/user', {
      params: {
        page: pagination.page,
        size: pagination.size,
        ...searchForm
      }
    })
    userList.value = response.data.list
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 新增用户
const handleAdd = async () => {
  const formRef = userFormRef.value
  await formRef.validate()

  try {
    await request.post('/SM/user', userFormData)
    ElMessage.success('新增用户成功')
    fetchUsers()
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.message || '新增用户失败')
  }
}
```

## 交互设计

### 表单验证
- 用户名必填，3-20字符
- 真实姓名必填，2-10字符
- 所属组织必填
- 实时验证和提交验证

### 操作反馈
- 操作成功：绿色提示消息
- 操作失败：红色错误消息
- 加载状态：表格 loading 效果
- 删除确认：二次确认弹窗

## 扩展功能

### 待实现
1. **编辑用户**
   - 表单预填充
   - 更新用户信息
   - 状态切换

2. **批量操作**
   - 批量删除
   - 批量启用/禁用
   - 批量分配组织

3. **导入导出**
   - Excel 导入用户
   - 用户信息导出
   - 模板下载

## 注意事项

### 性能优化
- 大量数据时分页加载
- 防抖搜索避免频繁请求
- 组件卸载时取消请求

### 代码规范
- 使用 Composition API
- 提取复用逻辑
- 统一的错误处理
- 清晰的变量命名