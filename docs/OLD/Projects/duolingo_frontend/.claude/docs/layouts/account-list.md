# 账号管理列表页 布局说明

> 最后更新：2026-04-05
> 页面文件：`src/views/BDM/account/index.vue`

---

## 页面结构

- 页面容器
    - 卡片容器
        - 卡片头部
        - 搜索栏
            - 账号搜索
            - 手机号搜索
            - 客户ID搜索
            - 搜索按钮
            - 重置按钮
        - 数据表格
            - ID列
            - 用户名列
            - 昵称列
            - 组织列
            - 状态列
            - 手机号列
            - 邮箱列
            - 创建时间列
            - 操作列
                - 详情按钮
        - 分页器
- 新增账号弹窗（浮层）
    - 账号Tab
        - 账号输入
        - 密码输入
        - 备注输入
    - 手机号Tab
        - 手机号输入
        - 发送验证码按钮
        - 验证码输入
        - 备注输入
    - 底部按钮
        - 取消按钮
        - 验证按钮
        - 确定按钮

---

## 结构说明

### 页面容器
tag: .account-container
note: 页面根容器，全高布局

### 卡片容器
tag: .account-list
note: 主内容卡片区域，flex: 1 自适应高度

### 卡片头部
tag: .card-header
note: 卡片标题栏，左侧显示"账号管理"标题，右侧显示"新增账号"按钮

### 搜索栏
tag: .search-form
note: 行内表单搜索区，支持按账号/邮箱、手机号、客户ID三个维度筛选账号数据，含搜索和重置按钮

### 账号搜索
tag: el-form-item（label="账号"）
note: 输入框，支持按账号或邮箱号模糊搜索，可清空

### 手机号搜索
tag: el-form-item（label="手机号"）
note: 输入框，按手机号搜索，可清空

### 客户ID搜索
tag: el-form-item（label="客户ID"）
note: 输入框，按客户ID搜索，可清空

### 搜索按钮
tag: el-button（type="primary"）
note: 点击执行搜索，重置分页到第一页并刷新列表

### 重置按钮
tag: el-button
note: 点击清空所有搜索条件，重置分页并刷新列表

### 数据表格
tag: el-table
note: 账号列表主体表格，双击行可跳转至账号详情页，固定高度自适应视口

### ID列
tag: el-table-column（prop="id"）
note: 账号ID，宽度60px

### 用户名列
tag: el-table-column（prop="username"）
note: 用户名，渲染为可点击链接，点击跳转至账号详情页

### 昵称列
tag: el-table-column（prop="nickname"）
note: 用户昵称

### 组织列
tag: el-table-column（prop="organizationName"）
note: 所属组织名称

### 状态列
tag: el-table-column（label="状态"）
note: 账号状态标签，正常显示绿色 success 标签，已禁用显示红色 danger 标签

### 手机号列
tag: el-table-column（prop="phone"）
note: 绑定的手机号

### 邮箱列
tag: el-table-column（prop="email"）
note: 绑定的邮箱

### 创建时间列
tag: el-table-column（prop="createdAt"）
note: 账号创建时间，宽度170px

### 操作列
tag: el-table-column（label="操作"）
note: 行操作按钮区，固定在右侧，宽度130px

### 详情按钮
tag: .operation-buttons .el-button
note: 点击跳转到对应账号的详情页

### 分页器
tag: .container-pagination
note: 分页组件，background 模式，显示上一页/页码/下一页，右对齐

### 新增账号弹窗
tag: .el-dialog（title="新增账号"）
note: 新增账号对话框，宽度450px，包含账号和手机号两种添加方式，点击遮罩不关闭

### 账号Tab
tag: el-tab-pane（label="账号"）
note: 通过账号+密码方式新增，包含账号、密码、备注三个表单项

### 手机号Tab
tag: el-tab-pane（label="手机号"）
note: 通过手机号+验证码方式新增，包含手机号、验证码、备注三个表单项，切换Tab时自动清空另一Tab的输入

### 发送验证码按钮
tag: el-button（type="primary"）
note: 向手机号发送验证码

### 底部按钮
tag: .dialog-footer
note: 弹窗底部操作按钮组，右对齐排列。验证按钮用于校验账号凭证，确定按钮需验证通过后才可用
