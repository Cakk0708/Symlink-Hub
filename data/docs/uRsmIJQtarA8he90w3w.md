# Login 模块说明

## 模块定位

- **路径**: `/login`
- **别名**: 登录
- **所属**: 认证模块

## 功能概述

Login 模块负责用户登录认证功能，是系统的入口模块。提供用户名密码登录方式，成功后存储认证信息并跳转到系统主页。

## 核心功能

### 1. 登录表单
- **用户名输入**: 支持用户名/邮箱登录
- **密码输入**: 密码输入框，支持显示/隐藏
- **记住我**: 可选的记住登录状态
- **表单验证**: 实时验证用户名和密码格式

### 2. 认证处理
- **登录请求**: 调用后端登录接口
- **Token 存储**: 登录成功后存储 JWT Token
- **用户信息**: 存储用户基本信息到 localStorage
- **自动跳转**: 登录成功后跳转到 dashboard

### 3. 错误处理
- **错误提示**: 友好的错误消息提示
- **表单重置**: 错误后自动清空密码
- **验证反馈**: 实时的表单验证反馈

## 技术实现

### 表单验证
```javascript
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}
```

### 认证流程
```javascript
const handleLogin = async () => {
  try {
    loading.value = true
    const response = await request.post('/SM/user/login', {
      username: form.username,
      password: form.password
    })

    // 存储 token
    localStorage.setItem('token', response.token)
    localStorage.setItem('userinfo', JSON.stringify(response.user))

    // 跳转
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
```

## UI 设计

### 布局设计
- 居中卡片式布局
- 响应式设计适配各种屏幕
- Logo 和品牌展示区域
- 表单区域简洁明了

### 交互细节
- 输入框聚焦效果
- 按钮悬停和加载状态
- 键盘 Tab 键导航支持
- 回车键提交表单

## 安全考虑

### 前端安全
- 密码输入框使用 type="password"
- 登录失败不提示具体是用户名还是密码错误
- 清除自动填充的密码
- 使用 HTTPS 确保传输安全

### 存储安全
- Token 存储在 localStorage（项目当前做法）
- 考虑使用 httpOnly cookie 更安全（需后端支持）
- 设置合理的 Token 过期时间

## 开发注意事项

### 路由守卫
- 配置路由守卫检查认证状态
- 未登录用户自动重定向到登录页
- Token 过期自动跳转登录

### 代码规范
- 使用 Composition API
- 提取登录验证逻辑
- 统一错误处理
- 清理定时器和事件监听器