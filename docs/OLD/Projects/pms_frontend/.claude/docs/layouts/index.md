# 项目首页 布局说明

> 最后更新：2026-03-26
> 页面文件：`pages/index/index.vue`

---

## 页面结构

- 主容器
    - 页面标语
    - 搜索栏
    - 功能模块导航区
        - 项目入口卡片
        - 报表入口卡片
        - 后台入口卡片
    - 移动端切换头部
        - 标题切换下拉
        - 筛选按钮
    - 项目列表组件
- 新建项目弹窗（浮层）
    - 标题
        - 新建项目
        - 关闭按钮
    - 内容容器
        - 项目名称
        - 交付日期
        - 项目负责人
        - 项目难度系数
        - 客户
        - 机型
    - 项目模板选择容器
    - 操作按钮
        - 取消
        - 确认创建
- 项目枚举配置弹窗（浮层）
- 版本更新提示弹窗（浮层）
- 固定侧边栏
    - 用户头像
    - 帮助中心
    - 清除缓存
    - 退出登录
    - 折叠触发器

---

## 结构说明

### 主容器
tag: `.index-main`
note: 页面主体容器，最大宽度 1430px，居中显示，包含头部背景图

### 页面标语
tag: `.main-solgan`
note: 展示系统定位标语，位于页面顶部

### 搜索栏
tag: `index-search` 组件
note: 全局搜索入口，支持按项目名称模糊搜索

### 功能模块导航区
tag: `.main-module-swiper`
note: 三个快捷功能入口的展示区，PC 端横向滚动，移动端轮播

### 项目入口卡片
tag: `.module-task-item`
note: 项目管理模块入口，点击打开创建项目弹窗，包含图标、名称、描述和操作按钮

### 报表入口卡片
tag: `.module-task-item`
note: 报表统计模块入口，点击打开项目报表枚举选择弹窗

### 后台入口卡片
tag: `.module-task-item`
note: 系统后台管理入口，点击跳转到后台管理系统

### 移动端切换头部
tag: `taskAndProjectHead` 组件
note: 仅移动端显示，用于切换"项目列表"与"任务清单"视图

### 标题切换下拉
tag: `.progress-label-left .operation-btn .suspension`
note: 移动端专用的视图切换下拉菜单，包含"项目列表"和"任务清单"两个选项

### 筛选按钮
tag: `.project-filter`
note: 移动端筛选入口，点击打开右侧抽屉式筛选面板

### 项目列表组件
tag: `indexProject` 组件
note: 核心数据展示区，包含分类 Tab、多维度筛选、排序和项目列表表格

### 创建任务清单弹窗
tag: `task-createlists` 组件
note: 新建项目的浮层弹窗，支持选择项目模板、设置优先级等配置

### 项目枚举配置弹窗
tag: `project-enum` 组件
note: 报表模块的枚举选择弹窗，用于选择报表类型

### 版本更新提示弹窗
tag: `version-update-dialog` 组件
note: 应用版本更新提示浮层，显示新版本信息和更新操作

### 固定侧边栏
tag: `.fixedbar`
note: 页面右侧固定的快捷操作栏，支持展开/收起，PC 端鼠标悬停展开，移动端点击展开

### 用户头像
tag: `.fixedbar-item.avatar-item`
note: 显示当前登录用户的头像，无点击交互

### 帮助中心
tag: `.fixedbar-item`
note: 点击跳转到飞书帮助文档

### 清除缓存
tag: `.fixedbar-item`
note: 点击弹出确认对话框，确认后清除本地缓存并刷新页面

### 退出登录
tag: `.fixedbar-item.logout-item`
note: 点击退出当前登录账号，清除 token 和用户信息，跳转到登录页

### 折叠触发器
tag: `.fixedbar-trigger`
note: 侧边栏展开/收起的切换按钮，点击或鼠标悬停时展开侧边栏
