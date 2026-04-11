## 订单管理
地址: `/order`

### 模块名称
- 别名: `订单管理/订单列表/order list`

### 页面布局
- van-nav-bar: 顶部导航栏
  - title: 订单管理
  - right: 创建订单
- van-dropdown-menu: 筛选菜单
  - 状态筛选
  - 类型筛选
- van-search: 搜索框
- van-pull: 卡片列表
  - 卡片头部:
    - 左侧: 客户名称 + 订单编号
    - 右侧: 状态标签 + 类别标签
  - 卡片主体:
    - 账户 (账户昵称 + 用户名)
    - 创建时间
    - 计划时间
  - 卡片底部:
    - 进度信息 (已完成/计划数量 + 百分比)
    - 进度条
- tablist: 底部标签栏
  - 首页
  - 订单
  - 客户

## 订单详情
地址: `/order/{id}`

### 模块名称
- 别名: `订单详情`

### 页面布局
- van-nav-bar: 顶部导航栏（来自 DefaultLayout）
  - title: 订单详情
  - left: 返回按钮
  - right:
    - 当订单状态为 `waiting` 或 `doing` 时显示"..."菜单
    - 点击"..."呼出 van-popover，显示"取消订单"选项

- 操作按钮区:
  - 当订单状态为 `doing` 时显示"暂停"按钮
  - 当订单状态为 `pause` 时显示"继续"按钮

- van-cell-group inset title="订单信息":
  - 订单号 (#id)
  - 订单编号 (document.code)
  - 订单类型 (document.category + 标签)
  - 订单状态 (document.status + 标签)
  - 计划时间 (document.scheduleAt)

- van-cell-group inset title="执行进度":
  - 计划数量 (progressData.plannedQty)
  - 初始值 (progressData.beforeValue)
  - 已完成 (progressData.completedQty)
  - 持续时间 (progressData.planDuration 分钟)
  - 进度条 (百分比显示)

- van-cell-group inset title="关联信息":
  - 账户昵称 (relations.account.nickname)
  - 用户名 (relations.account.username)
  - 手机 (relations.account.phone)
  - 邮箱 (relations.account.email)
  - 账户备注 (relations.account.remark)
  - 客户名称 (relations.customer.name)
  - 客户编号 (relations.customer.code)
  - 组织名称 (relations.organization.name)
  - 组织编号 (relations.organization.code)

- van-cell-group inset title="其他信息":
  - 创建时间 (others.createdAt)
  - 更新时间 (others.updatedAt)

- van-tabbar: 底部标签栏（来自 DefaultLayout）
  - 首页
  - 订单
  - 客户
