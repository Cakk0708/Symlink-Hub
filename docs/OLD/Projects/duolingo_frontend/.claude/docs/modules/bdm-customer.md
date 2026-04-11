# BDM - 客户管理模块说明

## 模块定位

- **路径**: `/bdm/customer`
- **别名**: 客户管理
- **所属**: BDM (基础数据管理) 模块
- **父模块**: [BDM 模块](bdm.md)

## 功能概述

客户管理模块负责系统客户信息的全生命周期管理，包括客户列表展示、新增客户、查看客户详情等功能。客户是业务的基础单位，账号归属于客户。

## 核心功能

### 1. 客户列表
- **列表展示**: 表格形式展示所有客户
- **分页功能**: 支持大量数据的分页加载
- **搜索功能**: 支持按客户名搜索
- **批量操作**: 批量删除客户

### 2. 新增客户
- **表单验证**: 客户信息必填验证
- **提交功能**: 创建新客户
- **成功反馈**: 友好的成功提示
- **自动刷新**: 新增后自动刷新列表

### 3. 客户详情
- **基本信息**: 客户ID、客户名、类别
- **关联账号**: 展示该客户下的所有账号
- **操作记录**: 客户相关的操作历史

### 4. 客户类别
- **闲鱼客户**: GOOFISH 类型的客户
- **扩展支持**: 预留其他客户类型扩展

## 数据字段

### 客户信息结构
```javascript
{
  id: Number,           // 客户ID
  customer_name: String, // 客户名称
  customer_type: String, // 客户类型（如：GOOFISH）
  created_at: String,   // 创建时间
  updated_at: String,   // 更新时间
  status: String,       // 状态（活跃/非活跃）
  description: String,  // 客户描述（可选）
  contact_person: String, // 联系人（可选）
  phone: String,        // 联系电话（可选）
  email: String,        // 邮箱（可选）
  accounts: [          // 关联的账号列表
    {
      id: Number,
      username: String,
      platform: String,
      status: String
    }
  ]
}
```

## 技术实现

### 组件结构
```vue
<template>
  <div class="customer-management">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form inline>
        <el-form-item label="客户名称">
          <el-input
            v-model="searchForm.customer_name"
            placeholder="请输入客户名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="客户类型">
          <el-select v-model="searchForm.customer_type" clearable>
            <el-option label="闲鱼" value="GOOFISH" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作区域 -->
    <el-card class="action-card">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增客户
      </el-button>
      <el-button
        type="danger"
        :disabled="!selectedCustomers.length"
        @click="handleBatchDelete"
      >
        <el-icon><Delete /></el-icon>批量删除
      </el-button>
    </el-card>

    <!-- 客户列表 -->
    <el-card class="table-card">
      <el-table
        :data="customerList"
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="customer_name" label="客户名称" />
        <el-table-column prop="customer_type" label="客户类型">
          <template #default="{ row }">
            <el-tag>{{ row.customer_type === 'GOOFISH' ? '闲鱼' : row.customer_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '活跃' : '非活跃' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link @click="handleView(row)">详情</el-button>
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
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增客户' : '编辑客户'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="customerForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="客户名称" prop="customer_name">
          <el-input v-model="customerForm.customer_name" />
        </el-form-item>
        <el-form-item label="客户类型" prop="customer_type">
          <el-select v-model="customerForm.customer_type">
            <el-option label="闲鱼" value="GOOFISH" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="customerForm.status">
            <el-radio label="active">活跃</el-radio>
            <el-radio label="inactive">非活跃</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="customerForm.contact_person" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="customerForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="customerForm.email" />
        </el-form-item>
        <el-form-item label="客户描述" prop="description">
          <el-input
            v-model="customerForm.description"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
```

### 接口调用
```javascript
// 获取客户列表
const fetchCustomers = async () => {
  try {
    loading.value = true
    const response = await request.get('/BDM/customer', {
      params: {
        page: pagination.page,
        size: pagination.size,
        ...searchForm
      }
    })
    customerList.value = response.data.list
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取客户列表失败')
  } finally {
    loading.value = false
  }
}

// 新增客户
const handleSubmit = async () => {
  const formRef = formRef.value
  await formRef.validate()

  try {
    if (dialogType.value === 'add') {
      await request.post('/BDM/customer', customerForm)
      ElMessage.success('新增客户成功')
    } else {
      await request.patch(`/BDM/customer/${customerForm.id}`, customerForm)
      ElMessage.success('编辑客户成功')
    }
    dialogVisible.value = false
    fetchCustomers()
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
  }
}

// 删除客户
const handleDelete = async (customer) => {
  try {
    await ElMessageBox.confirm(`确定删除客户 "${customer.customer_name}" 吗？`, '提示', {
      type: 'warning'
    })
    await request.delete(`/BDM/customer/${customer.id}`)
    ElMessage.success('删除成功')
    fetchCustomers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
```

## 业务逻辑

### 客户状态管理
- **活跃**: 可以正常创建订单、使用账号
- **非活跃**: 限制创建订单功能，保留历史数据

### 数据关联规则
- 删除客户前检查是否有关联账号
- 有关联账号的客户不能直接删除
- 可以标记客户为非活跃状态

### 权限控制
- 客户数据查看权限
- 客户创建/编辑权限
- 客户删除权限（需要高级权限）

## 扩展功能

### 待实现
1. **客户导入**
   - Excel 批量导入客户
   - 模板下载
   - 导入结果反馈

2. **客户统计**
   - 客户数量统计
   - 客户类型分布
   - 客户活跃度分析

3. **客户标签**
   - 客户分类标签
   - 标签搜索功能
   - 标签管理界面

## 注意事项

### 性能优化
- 大量数据时的虚拟滚动
- 搜索防抖处理
- 分页缓存机制

### 数据安全
- 敏感信息加密存储
- 操作日志记录
- 数据备份机制