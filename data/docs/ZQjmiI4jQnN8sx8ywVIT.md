# Duolingo Backend 项目地图

本文档完整描述项目结构、模块命名、模块别名，涉及项目关键词必须在本文中找到对应模块。

## 架构设计

项目采用模块化设计，主要模块位于 `apps/` 目录下。
若模块提供了模块说明时必须阅读模块说明了解模块详细内容。

### SM（系统管理模块）

系统基础管理功能。

#### user
- 路径: `/SM/user`
- 别名: 用户管理/用户列表/用户/user
- 模块说明：`modules/sm-user.md`
- 接口文档：`api/sm-user.md`

#### organization
- 路径: `/SM/organizations`
- 别名: 组织管理/组织列表/组织
- 模块说明：`modules/sm-organization.md`
- 接口文档：`api/sm-organization.md`

#### dashboard
- 路径: `/SM/dashboard`
- 别名: 仪表盘/数据统计/首页
- 接口文档：`api/sm-dashboard.md`

**路由前缀：** `/SM/`

### BDM（业务数据管理模块）

客户和 Duolingo 账户管理。

#### customer
- 路径: `/BDM/customer`
- 别名: 客户管理/客户列表/客户
- 模块说明：`modules/bdm-customer.md`
- 接口文档：`api/bdm-customer.md`

#### account
- 路径: `/BDM/account`
- 别名: 账户管理/账户列表/账号管理/Duolingo账户
- 模块说明：`modules/bdm-account.md`
- 接口文档：`api/bdm-account.md`

##### account_credentials
- 路径: `/BDM/account/credentials`
- 别名: 账户凭证/账户验证

##### account_verification
- 路径: `/BDM/account/verification-codes`
- 别名: 验证码/发送验证码

#### package
- 路径: `/BDM/package`
- 别名: 套餐管理/套餐列表/套餐
- 模块说明：`modules/bdm-package.md`

##### package_simple
- 路径: `/BDM/package/simple`
- 别名: 套餐下拉/套餐简列

##### package_enums
- 路径: `/BDM/package/enums`
- 别名: 套餐枚举

##### package_gift
- 路径: `/BDM/package/<id>` (PATCH)
- 别名: 套餐赠品/赠品管理

**路由前缀：** `/BDM/`

### APS（异步处理系统模块）

订单管理和自动化任务调度。

#### order
- 路径: `/APS/order`
- 别名: 订单管理/订单列表/订单
- 模块说明：`modules/aps-order.md`
- 接口文档：`api/aps-order.md`

##### orders_enums
- 路径: `/APS/orders/enums`
- 别名: 订单枚举/订单状态

**路由前缀：** `/APS/`

### API（核心接口模块）

Duolingo 官方 API 集成。

#### duolingo
- 路径: `/API/test`
- 别名: Duolingo API/答题接口/测试接口/领奖励

**路由前缀：** `/API/`

### utils（工具模块）

公共工具和辅助函数。

#### code_generator
- 路径: `/utils/code_generator.py`
- 别名: 编码生成器/唯一编码/Code生成/generate_code

#### common
- 路径: `/utils/common.py`
- 别名: 通用工具/公共函数

#### redis
- 路径: `/utils/redis.py`
- 别名: Redis工具/Redis客户端/redis_service

## 核心业务流程

### 用户认证流程
1. 用户注册/登录（SM/user）
2. 系统返回 JWT Token（30天有效期）
3. 后续请求携带 Token 认证

### 客户管理流程
1. 创建客户（BDM/customer）
2. 自动生成客户编码（格式：C + 日期 + 序号）
3. 关联 Duolingo 账户（BDM/account）
4. 账户验证（支持用户名/手机/Token）

### 订单执行流程
1. 创建订单（APS/orders）
2. 订单状态：WAITING → IN_PROGRESS → COMPLETED/PAUSED/CANCELLED/ERROR
3. Celery 异步执行任务
4. 定时任务调度和检查

### 自动化任务类型
- **经验任务（EXP）**: 自动答题获取经验值
- **宝石任务（GEMS）**: 自动领取宝石奖励
- **3倍经验（3X_XP）**: 自动领取 3 倍经验加速
- **签到任务（SIGN）**: 自动签到打卡
