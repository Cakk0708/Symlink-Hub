# 账号管理详情页 布局说明

> 最后更新：2026-04-05
> 页面文件：`src/views/BDM/account/detail.vue`

---

## 页面结构

- 页面容器
    - 顶部导航栏
        - 左侧区域
            - 返回按钮
            - 页面标题
        - 右侧区域
            - 操作下拉菜单
                - 同步数据
                - 编辑备注
                - 启用/禁用账号
    - 文档信息卡片
        - 卡片头部
        - 描述列表
            - 账户编码
            - UUID
            - 用户名
            - 昵称
            - 邮箱
            - 手机号
    - 账号数据卡片
        - 卡片头部
        - 描述列表
            - 经验值
            - 宝石
            - 连续打卡天数
            - 今日是否打卡
            - 最后学习日期
    - 其他信息卡片
        - 卡片头部
        - 描述列表
            - 备注
            - 状态
            - 创建时间
            - 更新时间
- 编辑备注弹窗（浮层）
    - 备注输入
    - 底部按钮
        - 取消按钮
        - 确定按钮

---

## 结构说明

### 页面容器
tag: .account-detail-container
note: 页面根容器，灰白背景色，最小高度占满视口，内边距20px

### 顶部导航栏
tag: .page-header
note: 白色背景导航栏，左右布局（space-between），底部与内容区间隔20px

### 左侧区域
tag: .header-left
note: 导航栏左侧，包含返回按钮和页面标题，flex 水平排列，间距16px

### 返回按钮
tag: el-button（icon=ArrowLeft）
note: 点击返回账号管理列表页，路由跳转至 Account

### 页面标题
tag: .page-title
note: 显示"账号详情"标题文字，20px字号

### 右侧区域
tag: .header-right
note: 导航栏右侧，包含操作下拉菜单，flex 水平排列

### 操作下拉菜单
tag: el-dropdown
note: 点击触发的下拉菜单按钮，显示"操作"文字和向下箭头图标，通过 @command 统一分发操作

### 同步数据
tag: el-dropdown-item（command="sync"）
note: 调用 POST /BDM/account/{id}/sync 同步远端数据并刷新页面，图标 RefreshRight

### 编辑备注
tag: el-dropdown-item（command="edit"）
note: 点击打开编辑备注弹窗，图标 Edit

### 启用/禁用账号
tag: el-dropdown-item（command="enable"/"disable"）
note: 根据 others.disableFlag 动态切换，已禁用时显示"启用账号"（图标 Open），正常时显示"禁用账号"（图标 Close）。点击后弹出确认对话框

### 文档信息卡片
tag: .info-card（第一个）
note: 对应接口 document 分组，展示账户编码、UUID、用户名、昵称、邮箱、手机号，加载中显示 v-loading 动画

### 卡片头部
tag: .card-header
note: 卡片标题栏，显示"文档信息"标题

### 描述列表
tag: el-descriptions
note: 两列带边框的描述列表

### 账户编码
tag: el-descriptions-item（label="账户编码"）
note: 系统自动生成的账户编码（如 A20250308001），数据路径 document.code

### UUID
tag: el-descriptions-item（label="UUID"）
note: Duolingo 用户全局唯一标识符，数据路径 document.uuid

### 用户名
tag: el-descriptions-item（label="用户名"）
note: 账号登录用户名，数据路径 document.username

### 昵称
tag: el-descriptions-item（label="昵称"）
note: 用户在 Duolingo 的昵称，数据路径 document.nickname

### 邮箱
tag: el-descriptions-item（label="邮箱"）
note: 绑定的邮箱地址，数据路径 document.email

### 手机号
tag: el-descriptions-item（label="手机号"）
note: 绑定的手机号码，数据路径 document.phone

### 账号数据卡片
tag: .info-card（第二个）
note: 对应接口 accountData 分组，展示经验值、宝石、打卡相关数据

### 经验值
tag: el-descriptions-item（label="经验值"）
note: 账号当前经验值（EXP），数据路径 accountData.exp

### 宝石
tag: el-descriptions-item（label="宝石"）
note: 账号当前宝石数量（GEMS），数据路径 accountData.gems

### 连续打卡天数
tag: el-descriptions-item（label="连续打卡天数"）
note: 连续签到打卡天数，数据路径 accountData.checkInStreak

### 今日是否打卡
tag: el-descriptions-item（label="今日是否打卡"）
note: el-tag 标签显示，已打卡显示绿色 success 标签"是"，未打卡显示灰色 info 标签"否"，数据路径 accountData.isTodayCheckedIn

### 最后学习日期
tag: el-descriptions-item（label="最后学习日期"）
note: 最后一次签到日期，占两列宽度（span=2），数据路径 accountData.lastSign

### 其他信息卡片
tag: .info-card（第三个）
note: 对应接口 others 分组，展示备注、状态、时间信息

### 备注
tag: el-descriptions-item（label="备注"）
note: 账号备注信息，占两列宽度（span=2），无备注时显示"暂无备注"，数据路径 others.remark

### 状态
tag: el-descriptions-item（label="状态"）
note: 账号状态标签，正常显示绿色 success 标签，已禁用显示红色 danger 标签，数据路径 others.disableFlag

### 创建时间
tag: el-descriptions-item（label="创建时间"）
note: 账号在系统中的创建时间，数据路径 others.createdAt

### 更新时间
tag: el-descriptions-item（label="更新时间"）
note: 账号信息最后更新时间，占两列宽度（span=2），数据路径 others.updatedAt

### 编辑备注弹窗
tag: .el-dialog（title="编辑备注"）
note: 编辑账号备注的对话框，宽度450px，点击遮罩不关闭

### 备注输入
tag: el-input（type="textarea"）
note: 多行文本输入框，4行高度，用于输入或修改备注内容

### 底部按钮
tag: .dialog-footer
note: 弹窗底部操作按钮组，包含取消和确定按钮，右对齐排列
