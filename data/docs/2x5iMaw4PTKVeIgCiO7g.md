# APS - 订单管理模块说明

## 模块定位

- **路径**: `/aps/order`
- **别名**: 订单管理
- **所属**: APS (订单管理) 模块
- **父模块**: [APS 模块](aps.md)

## 功能概述

订单管理模块是系统的核心功能模块，负责订单的全生命周期管理。包括订单创建、状态管理、执行控制、结果展示等功能。订单是自动化服务的具体体现。

## 核心功能

### 1. 订单列表
- **列表展示**: 表格形式展示所有订单
- **分页功能**: 支持大量数据的分页加载
- **多条件搜索**:
  - 按客户名搜索
  - 按账号名搜索
  - 按订单类型筛选（EXP、GEMS、3X_XP、SIGN）
  - 按订单状态筛选（等待、进行中、完成、取消、错误）
  - 时间范围筛选
- **批量操作**: 批量删除、批量状态更新

### 2. 订单创建
- **账号搜索**: 支持自动补全的账号选择器
- **禁用账户过滤**: 加载账户下拉列表时自动过滤 `disableFlag: true` 的账户，禁用账户不可选
- **订单类型**: 四种订单类型可选
- **参数配置**: 根据订单类型显示不同参数
- **订单预览**: 创建前预览订单信息
- **表单验证**: 完整的表单验证机制

### 3. 订单状态管理
- **状态展示**: 清晰的状态标识
- **状态流转**:
  - 等待 → 进行中 → 完成
  - 支持暂停、重置、取消操作
- **批量更新**: 批量修改订单状态

### 4. 订单详情
- **折叠面板**: 结构化展示信息
- **基本信息**: 订单号、类型、状态等
- **执行数据**: 执行进度、结果数据
- **关联信息**: 客户、账号、组织信息
- **操作按钮**: 状态控制按钮

## 订单状态详解

### 状态定义
| 状态 | 描述 | 可执行操作 |
|------|------|-----------|
| **等待** (pending) | 订单已创建，等待执行 | 开始 |
| **进行中** (running) | 订单正在执行 | 暂停、完成、取消、重置 |
| **完成** (completed) | 订单执行成功 | 无 |
| **取消** (cancelled) | 订单被取消 | 无 |
| **错误** (error) | 执行过程出错 | 重置 |

### 状态颜色标识
- **等待**: 灰色
- **进行中**: 蓝色
- **完成**: 绿色
- **取消**: 红色
- **错误**: 橙色

## 订单类型参数

### EXP (经验值)
```javascript
{
  type: 'EXP',
  name: '经验值',
  params: {
    target_exp: Number,    // 目标经验值
    daily_limit: Number   // 每日上限
  }
}
```

### GEMS (宝石)
```javascript
{
  type: 'GEMS',
  name: '宝石',
  params: {
    target_gems: Number,    // 目标宝石数
    daily_limit: Number    // 每日上限
  }
}
```

### 3X_XP (3倍经验)
```javascript
{
  type: '3X_XP',
  name: '3倍经验',
  params: {
    duration: Number,       // 持续天数
    target_exp: Number     // 目标经验值
  }
}
```

### SIGN (签到)
```javascript
{
  type: 'SIGN',
  name: '签到',
  params: {
    sign_days: Number      // 签到天数
  }
}
```

## 技术实现

### 组件结构
```vue
<template>
  <div class="order-management">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form inline>
        <el-form-item label="客户">
          <el-input
            v-model="searchForm.customer_name"
            placeholder="客户名"
            clearable
          />
        </el-form-item>
        <el-form-item label="账号">
          <el-input
            v-model="searchForm.username"
            placeholder="账号名"
            clearable
          />
        </el-form-item>
        <el-form-item label="订单类型">
          <el-select v-model="searchForm.order_type" clearable>
            <el-option label="经验值" value="EXP" />
            <el-option label="宝石" value="GEMS" />
            <el-option label="3倍经验" value="3X_XP" />
            <el-option label="签到" value="SIGN" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" clearable>
            <el-option label="等待" value="pending" />
            <el-option label="进行中" value="running" />
            <el-option label="完成" value="completed" />
            <el-option label="取消" value="cancelled" />
            <el-option label="错误" value="error" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作区域 -->
    <el-card class="action-card">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>创建订单
      </el-button>
      <el-button
        type="danger"
        :disabled="!selectedOrders.length"
        @click="handleBatchDelete"
      >
        <el-icon><Delete /></el-icon>批量删除
      </el-button>
    </el-card>

    <!-- 订单列表 -->
    <el-card class="table-card">
      <el-table
        :data="orderList"
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="customer_name" label="客户" width="120" />
        <el-table-column prop="username" label="账号" width="120" />
        <el-table-column prop="order_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag>{{ getOrderTypeName(row.order_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="params" label="参数" min-width="200">
          <template #default="{ row }">
            <span>{{ formatParams(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="100">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress || 0"
              :status="getProgressStatus(row.status)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link @click="handleView(row)">详情</el-button>
            <el-button
              link
              type="primary"
              @click="handleControl(row)"
              :disabled="!canControl(row)"
            >
              {{ getControlText(row) }}
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

    <!-- 创建订单弹窗 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建订单"
      width="600px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="客户" prop="customer_id">
          <el-select
            v-model="createForm.customer_id"
            placeholder="请选择客户"
            filterable
            @change="handleCustomerChange"
          >
            <el-option
              v-for="customer in customerList"
              :key="customer.id"
              :label="customer.customer_name"
              :value="customer.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="执行账号" prop="account_id">
          <el-select
            v-model="createForm.account_id"
            placeholder="请选择执行账号"
            filterable
            :disabled="!accountOptions.length"
          >
            <el-option
              v-for="account in accountOptions"
              :key="account.id"
              :label="account.username"
              :value="account.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="订单类型" prop="order_type">
          <el-select v-model="createForm.order_type" @change="handleTypeChange">
            <el-option label="经验值" value="EXP" />
            <el-option label="宝石" value="GEMS" />
            <el-option label="3倍经验" value="3X_XP" />
            <el-option label="签到" value="SIGN" />
          </el-select>
        </el-form-item>

        <!-- 动态参数表单 -->
        <template v-if="createForm.order_type">
          <el-form-item
            v-if="createForm.order_type === 'EXP'"
            label="目标经验值"
            prop="target_exp"
          >
            <el-input-number v-model="createForm.params.target_exp" :min="1" />
          </el-form-item>
          <el-form-item
            v-if="createForm.order_type === 'EXP' || createForm.order_type === 'GEMS'"
            label="每日上限"
            prop="daily_limit"
          >
            <el-input-number v-model="createForm.params.daily_limit" :min="1" />
          </el-form-item>
          <el-form-item
            v-if="createForm.order_type === '3X_XP'"
            label="持续天数"
            prop="duration"
          >
            <el-input-number v-model="createForm.params.duration" :min="1" />
          </el-form-item>
          <el-form-item
            v-if="createForm.order_type === '3X_XP'"
            label="目标经验值"
            prop="target_exp"
          >
            <el-input-number v-model="createForm.params.target_exp" :min="1" />
          </el-form-item>
          <el-form-item
            v-if="createForm.order_type === 'SIGN'"
            label="签到天数"
            prop="sign_days"
          >
            <el-input-number v-model="createForm.params.sign_days" :min="1" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitCreate">确定</el-button>
      </template>
    </el-dialog>

    <!-- 订单详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="订单详情"
      width="800px"
      fullscreen
    >
      <order-detail :order="selectedOrder" />
    </el-dialog>
  </div>
</template>
```

### 接口调用
```javascript
// 获取订单列表（响应兼容处理）
const fetchOrders = async () => {
  try {
    loading.value = true
    const response = await request.get('/APS/orders', {
      params: {
        page: pagination.page,
        size: pagination.size,
        ...searchForm,
        start_date: dateRange.value?.[0],
        end_date: dateRange.value?.[1]
      }
    })
    // 兼容 response.data?.items 和 response.items 两种响应格式
    const items = response?.items || response?.data?.items || []
    const pageData = response?.pagination || response?.data?.pagination || {}
    orderList.value = items
    pagination.total = pageData.total
  } catch (error) {
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

// 创建订单
const handleSubmitCreate = async () => {
  const formRef = createFormRef.value
  await formRef.validate()

  try {
    await request.post('/APS/orders', {
      customer_id: createForm.customer_id,
      account_id: createForm.account_id,
      order_type: createForm.order_type,
      params: createForm.params
    })
    ElMessage.success('创建订单成功')
    createDialogVisible.value = false
    fetchOrders()
  } catch (error) {
    ElMessage.error(error.message || '创建订单失败')
  }
}

// 控制订单状态
const handleControl = async (order) => {
  try {
    const action = getControlAction(order)
    await request.patch(`/APS/orders/${order.id}`, {
      action: action
    })
    ElMessage.success(`${getControlText(order)}成功`)
    fetchOrders()
  } catch (error) {
    ElMessage.error(error.message || `${getControlText(order)}失败`)
  }
}

// 删除订单
const handleDelete = async (order) => {
  try {
    await ElMessageBox.confirm(`确定删除订单 ${order.order_no} 吗？`, '提示', {
      type: 'warning'
    })
    await request.delete(`/APS/orders/${order.id}`)
    ElMessage.success('删除成功')
    fetchOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
```

## 业务逻辑

### 订单创建流程
1. 选择客户
2. 加载该客户的账号列表（自动过滤禁用账户）
3. 选择执行账号
4. 选择订单类型
5. 填写订单参数
6. 提交创建订单

### 订单状态控制
- **开始**: 等待状态 → 进行中
- **暂停**: 进行中 → 等待（保留进度）
- **完成**: 进行中 → 完成
- **重置**: 任何状态（除完成）→ 等待（清空进度）
- **取消**: 任何状态 → 取消

### 参数验证
- 客户必须存在且有效
- 账号必须属于该客户
- 参数必须符合对应订单类型要求
- 数值参数必须为正整数

## 扩展功能

### 待实现
1. **订单模板**
   - 保存常用订单配置
   - 快速创建模板订单
   - 模板管理界面

2. **定时任务**
   - 定时创建订单
   - 定时检查订单状态
   - 定时清理过期订单

3. **数据统计**
   - 订单完成率统计
   - 执行时间分析
   - 客户订单分布

4. **批量操作**
   - 批量创建订单
   - 批量状态更新
   - 批量导出数据

## 注意事项

### 性能优化
- 大数据量列表虚拟滚动
- 搜索条件防抖处理
- 分页加载优化

### 数据安全
- 订单数据加密存储
- 敏感信息脱敏显示
- 操作日志完整记录

### 用户体验
- 加载状态清晰显示
- 操作反馈及时准确
- 错误提示友好明了