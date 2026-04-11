# PMS 认证架构快速参考

## 核心函数速查

### 环境判断

```javascript
// 方法一：直接调用（推荐）
function checkFeishuContainer() {
    const ua = navigator.userAgent || ''
    return ua.includes('Lark') || ua.includes('Feishu') || typeof tt !== 'undefined'
}

// 方法二：使用 Detector
import { EnvironmentDetector } from '@/common/auth/core/EnvironmentDetector.js'
const detector = new EnvironmentDetector()
detector.isInFeishuContainer()
```

### Token 检查

```javascript
import { hasValidToken } from '@/common/auth'

// ✅ 正确：使用 hasValidToken()
if (hasValidToken()) {
    // 有有效 token
}

// ❌ 错误：不要直接访问 token
if (getToken()?.access_token) { }
```

### 登录入口

```javascript
import { oauth_login } from '@/common/global.js'

// 自动根据环境选择登录方式
await oauth_login()
```

---

## 常见问题速查

| 问题 | 检查项 | 解决方案 |
|------|---------|----------|
| 无限登录 | hasValidToken() 使用 `!!` | 改用 `Boolean()` |
| 无限登录 | refreshToken() 无条件调用 onLogin | 先检查 hasValidToken() |
| 浏览器跳转错误 | 未显示登录选择页 | 调用 showLoginSelectionPage() |
| getToken 空 | uni.storage 返回空字符串 | 优先使用 localStorage |
| 401 错误 | 未正确处理刷新 | 使用 handle401() |

---

## 修改认证代码前的检查清单

修改任何认证相关代码前，确认：

- [ ] 是否考虑了飞书容器和浏览器两种环境？
- [ ] 是否正确使用 `hasValidToken()` 检查而非直接访问 token？
- [ ] 是否可能导致无限登录循环？
- [ ] Token 存储是否同时考虑 localStorage 和 uni.storage？
- [ ] 是否正确处理了空字符串、null、undefined 等边界情况？
- [ ] 新增 Provider 是否继承了 LoginProvider 基类？
- [ ] 是否正确验证了 state 参数防 CSRF？
- [ ] 是否在回调中正确指定了 provider 参数？

---

## Token 数据结构

### 当前格式（正确）

```javascript
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",  // JWT，7天有效
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."  // JWT，长期有效
}
```

### 旧格式（已废弃）

```javascript
{
    "token_type": "Bearer",      // ❌ 不再使用
    "access_token": "...",
    "timestamp": 1234567890         // ❌ 不再使用
}
```

**注意**：不要再使用 `token.timestamp` 来判断 token 是否有效，应使用 `hasValidToken()`。

---

## 文件位置速查

| 功能 | 文件路径 |
|------|----------|
| Token 管理 | `common/auth.js` |
| 登录入口 | `common/global.js` |
| Provider 注册 | `common/auth/core/ProviderRegistry.js` |
| 环境检测 | `common/auth/core/EnvironmentDetector.js` |
| 登录选择页 | `pages/auth/login-select.vue` |
| 回调处理页 | `pages/auth/callback.vue` |
| 首页逻辑 | `pages/index/index.vue` |

---

## 后端接口说明

### 登录接口

```
POST /auth/login

请求体：
{
  "code": "飞书授权码",      // 必填
  "provider": "feishu"         // 可选，默认飞书
}

响应体：
{
  "data": {
    "token": {
      "access_token": "JWT访问令牌",
      "refresh_token": "JWT刷新令牌"  // 注意：字段名是 refresh_token
    },
    "userinfo": { ... },
    "config": { ... }
  }
}
```

### 刷新接口

```
POST /auth/refresh

请求体：
{
  "refresh": "refresh_token"  // 注意：字段名是 refresh 而非 refresh_token
}

响应体：
{
  "data": {
    "access_token": "新JWT",
    "refresh_token": "新refresh_token"  // 可能不返回，复用旧的
  }
}
```

---

## 飞书开发者后台配置

### 需要配置的回调 URL

**开发环境**：
```
http://localhost:8001/pages/auth/callback
http://localhost:8006/pages/auth/callback
http://localhost:88/pages/auth/callback
```

**测试环境**：
```
https://pms-test.lingyang-electronics.com/pages/auth/callback
```

**生产环境**：
```
https://pms.lingyang-electronics.com/pages/auth/callback
```

### 配置步骤

1. 登录 [飞书开放平台](https://open.feishu.cn/app)
2. 进入应用 **凭证与基础信息**，获取 `App ID` 和 `App Secret`
3. 进入 **安全设置** > **重定向 URL**
4. 添加上述回调地址（每行一个）
5. 保存配置

---

## 环境特征速查

| 环境 | UserAgent 特征 | 全局对象 | 登录方式 |
|------|----------------|----------|----------|
| 飞书容器（H5） | Lark, Feishu | `tt` | tt.requestAuthCode |
| 飞书小程序 | Lark, Feishu | `tt` | tt.requestAuthCode |
| 企业微信 | wxwork | `wx` | wx.qy.login |
| 钉钉 | DingTalk | `dd` | dd.runtime.permission.requestAuthCode |
| 浏览器 | Chrome, Safari, Firefox | - | OAuth 2.0 |
