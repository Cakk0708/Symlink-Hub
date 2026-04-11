# BDM (基础数据管理) 模块说明

## 模块定位

- **路径**: `/bdm`
- **别名**: 基础数据管理
- **所属**: 核心业务模块

## 功能概述

BDM (Basic Data Management) 模块是系统的基础数据管理中心，负责客户数据、账号数据等核心业务数据的管理。这些数据是订单管理等业务功能的基础。

## 核心功能

### 1. 客户管理
- **客户信息管理**: 维护客户基本信息
- **客户类别管理**: 支持多种客户类型（如闲鱼客户）
- **批量操作**: 支持批量删除等操作
- **搜索功能**: 多条件搜索客户信息

### 2. 账号管理
- **账号信息管理**: 管理各类平台账号
- **账号验证**: 支持账号密码验证、手机号验证码两种方式
- **信息同步**: 账号信息同步功能
- **多维度搜索**: 支持用户名、昵称等多条件搜索

### 3. 数据关联
- **客户-账号关联**: 客户与账号的关联关系
- **组织架构**: 基于组织的数据管理
- **数据同步**: 确保数据的一致性

## 模块结构

```
BDM/
├── index.vue          # BDM 模块主页
├── customer/          # 客户管理
│   └── index.vue      # 客户列表
└── account/           # 账号管理
    └── index.vue      # 账号列表
```

## 技术实现

### 路由配置
```javascript
{
  path: '/bdm',
  component: Layout,
  meta: { title: '基础数据', icon: 'DataLine' },
  children: [
    {
      path: 'customer',
      name: 'CustomerManagement',
      component: () => import('@/views/BDM/customer/index.vue'),
      meta: { title: '客户管理', icon: 'User' }
    },
    {
      path: 'account',
      name: 'AccountManagement',
      component: () => import('@/views/BDM/account/index.vue'),
      meta: { title: '账号管理', icon: 'UserFilled' }
    }
  ]
}
```

### 数据接口
#### 客户管理接口
- `GET /BDM/customer` - 获取客户列表
- `POST /BDM/customer` - 创建客户
- `DELETE /BDM/customer` - 删除客户
- `GET /BDM/customer/{id}` - 获取客户详情

#### 账号管理接口
- `GET /BDM/account` - 获取账号列表
- `POST /BDM/account` - 创建账号
- `PATCH /BDM/account/{id}` - 更新账号
- `GET /BDM/account/{id}` - 获取账号详情
- `POST /BDM/account/verification-codes` - 发送验证码
- `POST /BDM/account/credentials/verify` - 验证账号凭证

## 业务逻辑

### 数据关系
- **客户**: 业务对象，可以被多个账号关联
- **账号**: 具体执行任务的账号，属于某个客户
- **订单**: 基于账号创建的任务订单

### 数据流向
1. 客户管理 -> 维护客户基础信息
2. 账号管理 -> 为客户创建和管理执行账号
3. 订单管理 -> 使用账号创建任务订单

## 开发指南

### 添加新数据类型
1. 在 `views/BDM/` 下创建新模块
2. 实现对应的 CRUD 接口
3. 创建路由配置
4. 更新 BDM 主页导航

### 数据验证
- 客户信息必填字段验证
- 账号信息格式验证
- 关联数据存在性验证

## 扩展规划

### 数据类型扩展
1. **商品管理** (预留)
   - 商品信息维护
   - 商品分类管理
   - 价格策略设置

2. **模板管理** (预留)
   - 订单模板
   - 批量任务模板
   - 消息模板

3. **字典管理** (预留)
   - 系统字典维护
   - 业务字典管理
   - 数据标准化

### 功能增强
1. **数据导入导出**
   - Excel 数据导入
   - 数据导出功能
   - 数据模板下载

2. **数据校验**
   - 数据完整性检查
   - 重复数据检测
   - 数据质量评估

## 注意事项

### 性能优化
- 大量数据的分页加载
- 搜索条件的缓存
- 组件的懒加载

### 数据安全
- 敏感数据加密存储
- 操作日志记录
- 权限控制精细化