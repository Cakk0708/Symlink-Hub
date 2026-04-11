# BDM - 账号管理模块说明

## 模块定位

- **路径**: `/bdm/account`
- **别名**: 账号管理
- **所属**: BDM (基础数据管理) 模块
- **父模块**: [BDM 模块](bdm.md)

## 功能概述

账号管理模块负责系统所有平台账号的全生命周期管理，包括账号列表展示、新增账号、编辑账号等功能。账号是执行订单任务的具体执行者，归属于特定客户。

## 核心功能

### 1. 账号列表
- **列表展示**: 表格形式展示所有账号
- **状态标识**: 显示账号禁用/正常状态（`el-tag` 标签）
- **分页功能**: 支持大量数据的分页加载
- **多条件搜索**: 用户名、昵称、邮箱、手机号等
- **高级搜索**: 支持组合条件搜索
- **批量操作**: 批量删除账号
- **禁用/启用**: 操作列支持一键禁用或启用账号（`PATCH /BDM/account/{id}/disable`）

### 2. 新增账号
- **两种验证方式**:
  - 账号密码验证
  - 手机号验证码验证
- **表单验证**: 实时验证账号信息
- **客户关联**: 必须选择所属客户
- **自动同步**: 创建后同步账号信息

### 3. 账号编辑
- **信息更新**: 修改账号基本信息
- **状态切换**: 启用/禁用账号
- **密码重置**: 重置账号密码
- **信息同步**: 重新同步账号数据

### 4. 账号详情
- **完整信息**: 显示账号的所有字段
- **关联客户**: 显示所属客户信息
- **使用统计**: 账号使用次数、成功率等
- **操作记录**: 账号相关的历史操作

### 5. 信息同步
- **手动同步**: 主动触发账号信息同步
- **自动同步**: 创建后自动同步
- **同步状态**: 显示同步结果和状态

## 数据字段

### 账号信息结构
```javascript
{
  id: Number,                    // 账号ID
  customer_id: Number,           // 所属客户ID
  username: String,              // 用户名（登录名）
  nickname: String,              // 昵称
  email: String,                 // 邮箱
  phone: String,                 // 手机号
  platform: String,              // 平台类型（如：闲鱼）
  password: String,              // 密码（加密存储）
  status: String,                // 状态（active/inactive）
  exp: Number,                   // 经验值
  gems: Number,                  // 宝石数量
  last_sign_in: String,          // 最后签到时间
  last_sign_in_days: Number,     // 连续签到天数
  is_signed_in_today: Boolean,   // 今日是否已签到
  created_at: String,            // 创建时间
  updated_at: String,            // 更新时间
  customer_info: {               // 关联的客户信息
    id: Number,
    customer_name: String,
    customer_type: String
  }
}
```

## 技术实现

### 组件结构
```vue
<template>
  <div class="account-management">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form inline>
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="用户名" clearable />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="searchForm.nickname" placeholder="昵称" clearable />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="searchForm.email" placeholder="邮箱" clearable />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="searchForm.phone" placeholder="手机号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" clearable>
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
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
        <el-icon><Plus /></el-icon>新增账号
      </el-button>
      <el-button
        type="danger"
        :disabled="!selectedAccounts.length"
        @click="handleBatchDelete"
      >
        <el-icon><Delete /></el-icon>批量删除
      </el-button>
    </el-card>

    <!-- 账号列表 -->
    <el-card class="table-card">
      <el-table
        :data="accountList"
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="nickname" label="昵称" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="150" />
        <el-table-column prop="phone" label="手机号" min-width="120" />
        <el-table-column prop="customer_info.customer_name" label="所属客户" min-width="120" />
        <el-table-column prop="exp" label="经验值" width="80" />
        <el-table-column prop="gems" label="宝石" width="80" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_sign_in_days" label="连续签到" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.last_sign_in_days > 0" type="warning">
              {{ row.last_sign_in_days }}天
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link @click="handleView(row)">详情</el-button>
            <el-button link @click="handleEdit(row)">编辑</el-button>
            <el-button
              link
              type="primary"
              @click="handleSync(row)"
              :loading="syncingIds.includes(row.id)"
            >
              同步
            </el-button>
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
      :title="dialogType === 'add' ? '新增账号' : '编辑账号'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="accountForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="所属客户" prop="customer_id">
          <el-select
            v-model="accountForm.customer_id"
            placeholder="请选择客户"
            filterable
          >
            <el-option
              v-for="customer in customerList"
              :key="customer.id"
              :label="customer.customer_name"
              :value="customer.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="用户名" prop="username">
          <el-input v-model="accountForm.username" />
        </el-form-item>

        <el-form-item label="验证方式" v-if="dialogType === 'add'">
          <el-radio-group v-model="verifyType">
            <el-radio label="password">账号密码验证</el-radio>
            <el-radio label="sms">手机号验证码</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 账号密码验证 -->
        <template v-if="verifyType === 'password'">
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="accountForm.password"
              type="password"
              show-password
            />
          </el-form-item>
        </template>

        <!-- 手机号验证码验证 -->
        <template v-else-if="verifyType === 'sms'">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="accountForm.phone">
              <template #append>
                <el-button
                  :disabled="!!cooldown"
                  @click="handleSendCode"
                >
                  {{ cooldown ? `${cooldown}s` : '发送验证码' }}
                </el-button>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="验证码" prop="verify_code">
            <el-input v-model="accountForm.verify_code" maxlength="6" />
          </el-form-item>
        </template>

        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="accountForm.nickname" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="accountForm.email" />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="accountForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
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
// 获取账号列表
const fetchAccounts = async () => {
  try {
    loading.value = true
    const response = await request.get('/BDM/account', {
      params: {
        page: pagination.page,
        size: pagination.size,
        ...searchForm
      }
    })
    accountList.value = response.data.list
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取账号列表失败')
  } finally {
    loading.value = false
  }
}

// 新增账号
const handleSubmit = async () => {
  const formRef = formRef.value
  await formRef.validate()

  try {
    if (dialogType.value === 'add') {
      if (verifyType.value === 'sms') {
        // 验证手机号验证码
        await request.post('/BDM/account/credentials/verify', {
          phone: accountForm.value.phone,
          code: accountForm.value.verify_code
        })
      }
      await request.post('/BDM/account', accountForm.value)
      ElMessage.success('新增账号成功')
    } else {
      await request.patch(`/BDM/account/${accountForm.value.id}`, accountForm.value)
      ElMessage.success('编辑账号成功')
    }
    dialogVisible.value = false
    fetchAccounts()
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
  }
}

// 发送验证码
const handleSendCode = async () => {
  try {
    await request.post('/BDM/account/verification-codes', {
      phone: accountForm.value.phone
    })
    ElMessage.success('验证码已发送')
    startCooldown()
  } catch (error) {
    ElMessage.error(error.message || '发送失败')
  }
}

// 同步账号信息
const handleSync = async (account) => {
  syncingIds.value.push(account.id)
  try {
    await request.post(`/BDM/account/${account.id}/sync`)
    ElMessage.success('同步成功')
    // 刷新列表
    fetchAccounts()
  } catch (error) {
    ElMessage.error(error.message || '同步失败')
  } finally {
    syncingIds.value = syncingIds.value.filter(id => id !== account.id)
  }
}
```

## 业务逻辑

### 账号验证流程
1. **账号密码验证**:
   - 输入账号密码
   - 直接调用登录接口验证
   - 验证成功后创建账号

2. **手机号验证码**:
   - 输入手机号
   - 发送验证码
   - 验证码验证通过
   - 自动登录获取账号信息

### 状态管理
- **正常** (`disableFlag: false`): 可以正常使用，前端显示绿色 `el-tag`
- **已禁用** (`disableFlag: true`): 限制使用，前端显示红色 `el-tag`；禁用账户无法被选为订单执行账号

### 禁用/启用操作
- 操作列提供「禁用/启用」按钮
- 点击后弹出 `ElMessageBox.confirm` 确认
- 调用 `PATCH /BDM/account/{id}/disable`，请求体 `{"disableFlag": true/false}`
- 操作成功后刷新列表

### 自动禁用机制
- 创建新账户时，若同组织内存在相同 UUID 的旧账户，后端自动将旧账户禁用

### 同步机制
- 创建后自动同步一次
- 手动触发重新同步
- 同步失败需要重试

## 扩展功能

### 待实现
1. **账号分组**
   - 按客户分组
   - 自定义分组
   - 分组批量操作

2. **账号统计**
   - 账号数量统计
   - 使用频率分析
   - 成功率统计

3. **批量导入**
   - Excel 批量导入
   - 模板下载
   - 导入错误提示

4. **账号导出**
   - 选择导出字段
   - 导出格式选择
   - 大数据分批导出

## 注意事项

### 性能优化
- 搜索防抖处理
- 大数据量虚拟滚动
- 分页加载优化

### 数据安全
- 密码加密存储
- 验证码防刷机制
- 操作日志记录

### 用户体验
- 加载状态提示
- 操作成功/失败反馈
- 友好的错误提示