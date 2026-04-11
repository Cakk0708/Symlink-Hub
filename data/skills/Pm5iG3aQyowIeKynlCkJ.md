---
name: pages-auth
description: |
  PMS 前端认证页面模块专家，负责 pages/auth/ 目录下的登录选择页面、OAuth 回调处理页面。

  **触发关键词**：登录选择页、OAuth 回调、callback、login-select、飞书登录、授权页面、ticket 兑换、state 验证

  **相关模块**：
  - 与 common/auth.js（Token 管理）配合
  - 与 common/global.js（登录入口）配合
  - 与 env.js（环境配置）配合

  **核心流程**：
  - 登录选择页：显示可用的登录方式（飞书、企业微信等）
  - OAuth 发起：跳转到后端 OAuth 接口
  - 回调处理：接收 ticket 并兑换 JWT token
  - 环境判断：自动识别飞书容器 vs 浏览器环境

  **已知问题**：state 验证失败、ticket 兑换接口响应结构、URL 末尾斜杠问题
---

# PMS 前端认证页面模块 (pages/auth)

## 简介

本技能专注于 PMS 项目 `pages/auth/` 目录下的认证页面模块，包括：

- **登录选择页面** (`login-select.vue`)：显示可用的登录方式
- **OAuth 回调页面** (`callback.vue`)：处理 OAuth 授权后的回调
- **双模式认证**：飞书容器静默授权 + 浏览器 OAuth 2.0 授权
- **环境自动检测**：自动识别运行环境并路由到正确的登录流程
- **已知问题解决**：记录了实施过程中遇到的所有问题和解决方案

## 触发条件 (When to use)

**核心触发词**：
- `login-select`、`callback`、`pages/auth`
- 登录选择页、授权页面、回调页面
- OAuth、ticket、state 验证

在以下情况下激活此技能：

- 用户询问"登录选择"、"授权页面"、"OAuth 回调"相关的问题
- 用户提到 `pages/auth/login-select.vue` 或 `pages/auth/callback.vue`
- 用户遇到登录页面显示、跳转、回调处理等问题
- 用户询问 OAuth 流程、ticket 兑换、state 验证
- 用户遇到"点击登录后没反应"、"回调页面报错"等问题
- 用户需要修改 `pages/auth/` 相关文件

## 详细指令

### 1. 架构理解

始终遵循以下核心原则：

```
┌─────────────────────────────────────────────────────────────┐
│                     前端自动判断环境                          │
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│    飞书容器环境       │         │    浏览器环境        │
│  checkFeishuContainer │         │   !checkFeishuContainer│
└─────────────────────┘         └─────────────────────┘
          │                               │
          ▼                               ▼
  tt.requestAuthCode            跳转登录选择页面
          │                          │
          │                          ▼
          │                  发起 OAuth 2.0 授权
          │                               │
          │                          后端 OAuth 接口
          │                               │
          └───────────────┬───────────────┘
                          ▼
                    后端处理并签发 JWT
                          │
                          ▼
                   保存 JWT token
                          │
                          ▼
                     进入系统
```

### 2. 关键文件位置

| 功能 | 文件路径 |
|------|----------|
| Token 管理 | `common/auth.js` |
| 登录入口 | `common/global.js` |
| 环境检测 | `common/auth/core/EnvironmentDetector.js` |
| Provider 注册 | `common/auth/core/ProviderRegistry.js` |
| 登录选择页面 | `pages/auth/login-select.vue` |
| OAuth 回调处理 | `pages/auth/callback.vue` |
| Provider 配置 | `common/config/authProviders.js` |
| 环境配置 | `env.js` |

### 3. OAuth 2.0 浏览器登录流程

🆕 **Since 2026-03-09**: 后端 OAuth 接口集成

#### 3.1 完整流程图

```
┌─────────────────┐
│  用户点击飞书登录  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 前端生成 state 并保存到 sessionStorage   │
│ state = 'feishu_xxx'                     │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 跳转到后端 OAuth 发起接口                │
│ /sm/auth/oauth/feishu/login             │
│ ?redirect_uri=/pages/auth/callback       │
│ &state=feishu_xxx                        │
└────────┬────────────────────────────────┘
         │
         ▼ (302 重定向)
┌─────────────────────────────────────────┐
│ 飞书授权页面                              │
│ user_oauth_authorize                     │
└────────┬────────────────────────────────┘
         │
         ▼ (用户授权)
┌─────────────────────────────────────────┐
│ 飞书回调后端                              │
│ /sm/auth/oauth/feishu/callback           │
│ ?code=xxx&state=yyy                      │
└────────┬────────────────────────────────┘
         │
         ▼ (后端处理)
    ┌──────────────────┐
    │ 1. 验证 state      │
    │ 2. code 换飞书token │
    │ 3. 获取用户信息     │
    │ 4. 生成 JWT token  │
    │ 5. 生成 ticket     │
    │ 6. 缓存到 Redis    │
    └────────┬─────────┘
             │
             ▼ (302 重定向)
┌─────────────────────────────────────────┐
│ 前端回调页面                              │
│ /pages/auth/callback                     │
│ ?ticket=login_ticket_xxx                 │
│ &state=zzz                               │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 前端验证 state 存在                       │
│ (后端自生成 state，不验证匹配)            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 调用票据兑换接口                          │
│ POST /sm/auth/oauth/exchange-ticket      │
│ { ticket: "login_ticket_xxx" }           │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 后端返回 JWT token 和用户信息             │
│ { userinfo, tokenData }                  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 保存 token 并跳转到首页                    │
└─────────────────────────────────────────┘
```

#### 3.2 关键接口路径

| 接口用途 | 路径 | 方法 | 说明 |
|---------|------|------|------|
| OAuth 发起 | `/sm/auth/oauth/feishu/login` | GET | 后端重定向到飞书授权页 |
| OAuth 回调 | `/sm/auth/oauth/feishu/callback` | GET | 飞书自动调用 |
| 票据兑换 | `/sm/auth/oauth/exchange-ticket` | POST | 前端调用兑换 token |
| Token 刷新 | `/sm/auth/refresh` | POST | 刷新过期的 access token |
| 飞书容器登录 | `/sm/auth/login` | POST | 飞书容器内静默授权 |

#### 3.3 环境配置

所有 OAuth 相关接口使用 `oauthBaseUrl`：

```javascript
// env.js
const oauthTestBaseUrl = 'https://pms-test.lingyang-electronics.com'
const oauthProdBaseUrl = 'https://pms.lingyang-electronics.com'

// 开发环境、测试环境统一使用测试环境 OAuth API
h5Dev: { oauthBaseUrl: oauthTestBaseUrl }

// 生产环境使用生产环境 OAuth API
h5Prod: { oauthBaseUrl: oauthProdBaseUrl }
```

### 4. 已知问题与解决方案

#### 问题一：无限登录循环

**现象**：飞书容器内不断调用 `/auth/login` 接口

**根本原因**：
1. `hasValidToken()` 布尔逻辑错误
2. `refreshToken()` 无条件调用 `onLogin()`

**解决方案**：
```javascript
// auth.js - 使用 Boolean() 而非 !!
export function hasValidToken() {
    const token = getToken()
    return Boolean(token && (token.access_token || token.access))
}

// pages/index/index.vue - 先检查再调用
refreshToken(type){
    if (hasValidToken()) {
        // 有 token，直接刷新数据
    } else {
        // 无 token，才调用登录
        await this.onLogin()
    }
}
```

#### 问题二：浏览器环境跳转错误

**现象**：浏览器直接跳转飞书授权页，不显示选择页面

**解决方案**：
```javascript
// global.js - 浏览器环境先显示选择页
async function oauth_login() {
    if (checkFeishuContainer()) {
        initiateFeishuContainerLogin()
    } else {
        showLoginSelectionPage()  // 关键修复
    }
}
```

#### 问题三：H5 环境 getToken() 空字符串问题

**解决方案**：优先使用 localStorage，增强空值处理

```javascript
export function getToken() {
    // H5 环境下，优先使用 localStorage（更可靠）
    if (typeof localStorage !== 'undefined') {
        const lsToken = localStorage.getItem(TOKEN_KEY)
        if (lsToken) {
            try {
                const parsed = JSON.parse(lsToken)
                if (parsed && (parsed.access_token || parsed.access)) {
                    return parsed
                }
            } catch (e) {
                console.error('getToken ----- localStorage JSON 解析失败', e)
            }
        }
    }
    // 处理空字符串
    if (!token || token === '' || (typeof token === 'string' && token.trim() === '')) {
        return null
    }
    return token
}
```

#### 问题四：OAuth URL 末尾斜杠导致 302 失败

🆕 **Since 2026-03-09**

**现象**：后端返回 200 状态码（HTML 页面）而不是 302 重定向

**根本原因**：OAuth URL 路径末尾有斜杠 `/sm/auth/oauth/feishu/login/`

**解决方案**：
```javascript
// pages/auth/login-select.vue
// ❌ 错误
const oauthLoginUrl = `${config.oauthBaseUrl}/sm/auth/oauth/feishu/login/?redirect_uri=...`

// ✅ 正确
const oauthLoginUrl = `${config.oauthBaseUrl}/sm/auth/oauth/feishu/login?redirect_uri=...`
```

#### 问题五：state 验证失败

🆕 **Since 2026-03-09**

**现象**：
```
[callback] state 验证失败
received: 'lUuoUH-NlYVWp0tPizu3awumBTroGfEgz3cH0qKR4Eo'
saved: 'feishu_iu8wlqi7e4i_mmiv8d58'
```

**根本原因**：后端自己生成 state，不使用前端传递的 state 参数

**解决方案**：修改前端验证逻辑，只验证 state 存在性而不验证匹配
```javascript
// pages/auth/callback.vue
// ❌ 旧的验证逻辑（不适用）
const stateValid = this.validateState(options.state)
if (state !== savedState) {
    return false  // 会失败
}

// ✅ 新的验证逻辑
if (!options.state) {
    console.error('[callback] 后端未返回 state')
    return false
}
// 只验证存在性，不验证匹配
```

### 5. Token 数据结构

#### 当前格式

```javascript
{
    "access": "JWT访问令牌",    // 7天有效
    "refresh": "JWT刷新令牌"    // 长期有效
}
```

#### 旧格式（已废弃）

```javascript
{
    "access_token": "...",      // 使用 access 替代
    "refresh_token": "...",     // 使用 refresh 替代
    "token_type": "Bearer",     // 不再使用
    "timestamp": 1234567890     // 不再使用
}
```

**兼容处理**：代码同时支持新旧格式
```javascript
const accessToken = token?.access_token || token?.access
const refreshToken = token?.refresh_token || token?.refresh
```

### 6. 接口响应结构

#### 票据兑换接口响应

🆕 **Since 2026-03-09**

```javascript
// POST /sm/auth/oauth/exchange-ticket
{
  "code": 0,
  "msg": "success",
  "data": {
    "userinfo": {
      "id": 1,
      "nickname": "张三",
      "avatar": "...",
      "mobile": "13800138000"
    },
    "tokenData": {              // 注意：是 tokenData 不是 token
      "access": "eyJhbGci...",
      "refresh": "eyJhbGci..."
    }
  }
}
```

**注意**：
- 字段名是 `tokenData` 而非 `token`
- 不再返回 `config` 字段

### 7. 添加新 Provider 的步骤

当需要添加新平台（如企业微信、钉钉）时：

1. 创建 `common/auth/providers/{Platform}Provider.js`
2. 继承 `LoginProvider` 基类
3. 实现必需方法：`detectEnvironment()`, `initiateLogin()`, `handleCallback()`
4. 在 `authProviders.js` 中注册
5. 在飞书/企业微信/钉钉开发者后台配置 OAuth 回调 URL

### 8. 修改认证相关代码前的检查清单

- [ ] 是否考虑了飞书容器和浏览器两种环境？
- [ ] 是否正确使用 `hasValidToken()` 检查而非直接访问 token？
- [ ] 是否可能导致无限登录循环？
- [ ] Token 存储是否同时考虑 localStorage 和 uni.storage？
- [ ] 是否正确处理了空字符串、null、undefined 等边界情况？
- [ ] OAuth URL 是否正确（无末尾斜杠，包含 state 参数）？
- [ ] 是否正确处理了后端自生成 state 的情况？
- [ ] 是否使用了正确的接口响应字段（tokenData 而非 token）？

## 示例 (Examples)

### 示例 1：用户询问如何添加企业微信登录

**用户**：我想添加企业微信登录支持，应该怎么改？

**助手**：基于 PMS 认证架构，添加企业微信登录需要：

1. 创建 `common/auth/providers/WeWorkProvider.js`，继承 `LoginProvider` 基类
2. 实现三个核心方法：
   - `detectEnvironment()`: 检测是否在企业微信容器内
   - `initiateLogin()`: 发起企业微信 OAuth 2.0 授权
   - `handleCallback()`: 处理授权回调
3. 在 `common/config/authProviders.js` 中注册新 Provider
4. 在企业微信开发者后台配置回调 URL
5. 在 `pages/auth/login-select.vue` 中会自动显示新的登录选项

需要我为你创建 WeWorkProvider 的完整代码吗？

---

### 示例 2：用户遇到登录循环问题

**用户**：我的页面一直在调用登录接口，怎么办？

**助手**：这是 PMS 认证架构中的已知问题一：无限登录循环。请检查：

1. **检查 `hasValidToken()` 逻辑**：
   ```bash
   grep -n "hasValidToken" common/auth.js
   ```
   确认使用 `Boolean(token && (token.access_token || token.access))`

2. **检查 `refreshToken()` 函数**：
   ```bash
   grep -A 10 "refreshToken" pages/index/index.vue
   ```
   确认在调用 `onLogin()` 前先检查 `hasValidToken()`

3. **检查控制台日志**：确认是否有 token 但仍然触发登录

需要我帮你定位具体的问题代码位置吗？

---

### 示例 3：用户询问环境判断

**用户**：如何判断当前是在飞书容器还是浏览器？

**助手**：PMS 提供了标准的环境判断方法：

```javascript
// 方法一：使用全局函数（推荐）
function checkFeishuContainer() {
    const ua = navigator.userAgent || ''
    return ua.includes('Lark') || ua.includes('Feishu') || typeof tt !== 'undefined'
}

// 方法二：使用 EnvironmentDetector（Provider 模式）
import { EnvironmentDetector } from '@/common/auth/core/EnvironmentDetector.js'

const detector = new EnvironmentDetector()
if (detector.isInFeishuContainer()) {
    // 飞书容器环境
} else {
    // 浏览器环境
}
```

测试技巧：
- 飞书容器：UserAgent 包含 "Lark" 或 "Feishu"
- 浏览器：常规浏览器 UserAgent（Chrome, Safari, Firefox 等）

---

### 示例 4：用户遇到 OAuth 登录跳转问题

🆕 **Since 2026-03-09**

**用户**：点击飞书登录后，页面跳转了但后端返回 200 而不是重定向？

**助手**：这是问题四：OAuth URL 末尾斜杠导致后端路由匹配失败。

请检查 `pages/auth/login-select.vue:110`：

```javascript
// ❌ 错误（末尾有斜杠）
const oauthLoginUrl = `${config.oauthBaseUrl}/sm/auth/oauth/feishu/login/?redirect_uri=...`

// ✅ 正确
const oauthLoginUrl = `${config.oauthBaseUrl}/sm/auth/oauth/feishu/login?redirect_uri=...&state=${state}`
```

同时确保：
1. URL 中包含 `state` 参数
2. `redirect_uri` 正确编码
3. 使用 `oauthBaseUrl` 而非 `baseUrl`

---

### 示例 5：用户遇到 state 验证失败

🆕 **Since 2026-03-09**

**用户**：callback 页面提示 state 验证失败，但后端确实返回了 state？

**助手**：这是问题五：后端自己生成 state，前端无法验证匹配。

由于 PMS 后端的 OAuth 实现中，state 是由后端生成的，前端保存的 state 不会被使用。因此前端不应该验证 state 是否匹配，只需验证 state 是否存在。

请检查 `pages/auth/callback.vue:26-32`，确保验证逻辑是：

```javascript
// ✅ 正确的验证逻辑
if (!options.state) {
    console.error('[callback] 后端未返回 state')
    this.handleCallbackError('登录失败：后端响应异常')
    return
}

// ❌ 错误的验证逻辑（会导致失败）
if (options.state !== savedState) {
    console.error('[callback] state 验证失败')
    return
}
```

前端生成的 state 仍然需要传递给后端（作为 OAuth 发起 URL 参数），但验证时只检查后端是否返回了 state。
