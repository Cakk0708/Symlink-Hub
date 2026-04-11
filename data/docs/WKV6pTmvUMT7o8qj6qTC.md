# 认证机制

## 认证方案概览

PMS 前端使用 **飞书 OAuth 2.0 + JWT** 的认证方案。

### 核心组成
- **OAuth 提供者**：飞书开放平台
- **Token 类型**：JWT (JSON Web Token)
- **授权方式**：Authorization Code Flow

---

## 认证流程

### 1. 首次登录流程
```
用户打开应用
    ↓
检查本地 Token
    ↓ (无有效 Token)
检测运行环境
    ↓
├─ 飞书容器环境
│      ↓
│   tt.requestAuthCode()
│      ↓
│   调用 /sm/auth/login
│      ↓
│   返回 JWT Token
│
└─ 浏览器环境
     ↓
  跳转登录选择页
     ↓
  跳转飞书 OAuth 授权页
     ↓
  用户授权
     ↓
  回调到 /pages/auth/callback
     ↓
  用 ticket 兑换 JWT Token
```

### 2. Token 刷新流程
```
API 请求返回 401
    ↓
检查本地是否有有效 Token (可能被其他请求刷新)
    ↓ (无)
使用 refresh_token 刷新
    ↓ (成功)
保存新 Token，重试原请求
    ↓ (失败)
清除本地 Token，重新登录
```

---

## Token 数据结构

### Token 格式
```json
{
	"access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
	"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 旧格式兼容
```json
{
	"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
	"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 核心模块

### 1. Token 管理 (common/auth.js)

#### getToken()
获取当前存储的 Token

```javascript
import { getToken } from '@/common/auth'

const tokenData = getToken()
// 返回：{ access: "...", refresh: "..." } 或 null
```

**实现要点**：
- H5 环境优先使用 localStorage
- 兼容新旧两种 Token 格式
- 验证 Token 有效性

#### saveToken(tokenData)
保存 Token（双写）

```javascript
import { saveToken } from '@/common/auth'

saveToken({
	access: 'access_token_value',
	refresh: 'refresh_token_value'
})
```

**实现要点**：
- 同时写入 localStorage 和 uni.storage
- H5 环境双写确保可靠性

#### hasValidToken()
检查本地是否有有效 Token

```javascript
import { hasValidToken } from '@/common/auth'

if (hasValidToken()) {
	// 已登录
}
```

#### getAuthorizationHeader()
获取 Authorization 请求头

```javascript
import { getAuthorizationHeader } from '@/common/auth'

const header = getAuthorizationHeader()
// 返回："Bearer access_token_value"
```

#### refreshAccessToken()
刷新 access_token

```javascript
import { refreshAccessToken } from '@/common/auth'

try {
	const newToken = await refreshAccessToken()
} catch (error) {
	// 刷新失败
}
```

#### handle401()
统一的 401 处理

```javascript
import { handle401 } from '@/common/auth'

await handle401()
// 自动刷新 Token 或重新登录
```

---

### 2. 全局登录方法 (common/global.js)

#### oauth_login()
登录入口方法

```javascript
import global from '@/common/global'

const sign = await global.oauth_login()
// sign.data: 用户信息
// sign.tokenData: Token 数据
```

**实现流程**：
1. 检查本地是否有有效 Token
2. 检测运行环境
3. 飞书容器：使用 tt.requestAuthCode
4. 浏览器：跳转登录选择页
5. 调用后端接口获取 Token
6. 保存 Token 和用户信息

---

### 3. 认证模块 (common/auth/)

#### 核心类
- `LoginProvider`：登录提供者基类
- `ProviderRegistry`：提供者注册表
- `EnvironmentDetector`：环境检测器

#### OAuth 提供者
- `FeishuProvider`：飞书 OAuth 实现

#### 回调处理
- `CallbackHandler`：OAuth 回调处理

---

## 认证页面

### 1. 登录选择页
**位置**：`pages/auth/login-select.vue`

**功能**：
- 检测运行环境
- 显示可用的登录方式
- 跳转到对应的 OAuth 授权页

**实现要点**：
```javascript
// 保存返回地址
const storage = getOAuthStorage()
storage.setItem('oauth_return_url', returnUrl)

// 跳转 OAuth
uni.navigateTo({
	url: '/pages/auth/callback?action=feishu_oauth'
})
```

### 2. OAuth 回调页
**位置**：`pages/auth/callback.vue`

**功能**：
- 接收 OAuth 回调参数
- 验证 state 参数
- 调用后端接口兑换 Token
- 保存 Token 并返回

**实现要点**：
```javascript
async onLoad(options) {
	const { ticket, state } = options

	// 验证 state
	if (!this.validateState(state)) {
		uni.showToast({ title: 'state 验证失败', icon: 'none' })
		return
	}

	// 兑换 Token
	const res = await request({
		url: 'sm/auth/token-exchange',
		method: 'POST',
		data: { ticket, state }
	})

	// 保存 Token
	saveToken(res.data.data.tokenData)

	// 返回来源页面
	const returnUrl = storage.getItem('oauth_return_url')
	if (returnUrl) {
		uni.redirectTo({ url: returnUrl })
	} else {
		uni.switchTab({ url: '/pages/index/index' })
	}
}
```

---

## 环境检测

### 飞书容器检测
```javascript
function checkFeishuContainer() {
	const ua = navigator.userAgent || ''

	// 检查 UserAgent
	if (ua.includes('Lark') || ua.includes('Feishu')) {
		return true
	}

	// 检查全局对象
	if (typeof window !== 'undefined' && typeof window.tt !== 'undefined') {
		return true
	}

	return false
}
```

### 平台检测
```javascript
// H5 环境
if (typeof localStorage !== 'undefined') {
	// 使用 localStorage
}

// 小程序环境
if (typeof uni !== 'undefined') {
	// 使用 uni.storage
}
```

---

## Token 存储

### 存储策略
- **键名**：`betaToken`
- **位置**：localStorage + uni.storage 双写
- **用户信息键名**：`betaUserInfo`

### 为什么双写？
1. **H5 环境**：uni.getStorageSync 在模块加载时可能未初始化
2. **兼容性**：确保在各种情况下都能获取到 Token
3. **可靠性**：一个存储失败时可以使用另一个

### 存储示例
```javascript
// 保存 Token
uni.setStorageSync('betaToken', tokenData)
if (typeof localStorage !== 'undefined') {
	localStorage.setItem('betaToken', JSON.stringify(tokenData))
}

// 读取 Token
let token
if (typeof localStorage !== 'undefined') {
	const lsToken = localStorage.getItem('betaToken')
	token = lsToken ? JSON.parse(lsToken) : null
}
if (!token) {
	token = uni.getStorageSync('betaToken')
}
```

---

## 请求拦截

### 自动注入 Token
```javascript
// common/util/request.js

const authHeader = getAuthorizationHeader()

uni.request({
	url: baseUrl + options.url,
	method: options.method || 'GET',
	data: options.data || {},
	header: {
		'Content-Type': `application/${options.contentType == 'json' ? 'json' : 'x-www-form-urlencoded'}`,
		'Authorization': authHeader  // 自动注入
	},
	success: async (res) => {
		if (res.statusCode == 401) {
			await handle401()  // 自动刷新
			// 重试原请求
			const retryRes = await request(options)
			resolve(retryRes)
		}
	}
})
```

---

## 权限与认证

### 认证 vs 权限
- **认证**：确认用户身份（你是谁）
- **权限**：确认用户权限（你能做什么）

### 权限检查
```javascript
// 检查权限前先确认已认证
if (hasValidToken()) {
	if (permission(1001, 'project')) {
		// 有权限，执行操作
	}
}
```

---

## 常见场景

### 场景1：页面加载检查
```javascript
onShow() {
	if (hasValidToken()) {
		this.loadData()
	} else {
		this.onLogin().then(() => {
			this.loadData()
		})
	}
}
```

### 场景2：主动登录
```javascript
async handleLogin() {
	try {
		uni.showLoading({ title: '登录中...' })
		const sign = await global.oauth_login()
		uni.hideLoading()
		uni.showToast({ title: '登录成功', icon: 'success' })
	} catch (error) {
		uni.hideLoading()
		uni.showToast({ title: '登录失败', icon: 'error' })
	}
}
```

### 场景3：退出登录
```javascript
async handleLogout() {
	uni.showModal({
		title: '确认退出',
		content: '退出后需要重新登录',
		success: (res) => {
			if (res.confirm) {
				// 清除 Token
				uni.removeStorageSync('betaToken')
				if (typeof localStorage !== 'undefined') {
					localStorage.removeItem('betaToken')
				}
				// 清除用户信息
				uni.removeStorageSync('betaUserInfo')
				if (typeof localStorage !== 'undefined') {
					localStorage.removeItem('betaUserInfo')
				}
				// 返回首页
				uni.reLaunch({ url: '/pages/index/index' })
			}
		}
	})
}
```

---

## 错误处理

### 常见错误及处理

| 错误 | 原因 | 处理方式 |
|------|------|----------|
| 401 | Token 过期 | 自动刷新 Token |
| 403 | 权限不足 | 提示无权限 |
| state 验证失败 | CSRF 攻击 | 拒绝请求 |
| ticket 兑换失败 | 授权码无效 | 重新授权 |

### 错误提示
```javascript
uni.showToast({
	title: '登录已过期，请重新登录',
	icon: 'none',
	duration: 2000
})
```

---

## 安全注意事项

### Token 安全
- ✅ 使用 HTTPS 传输
- ✅ Token 存储在 localStorage
- ✅ 自动刷新机制
- ❌ 不要在 URL 中传递 Token
- ❌ 不要在 console.log 中输出完整 Token

### OAuth 安全
- ✅ 使用 state 参数防止 CSRF
- ✅ 验证回调来源
- ✅ ticket 一次性使用
- ❌ 不要泄露 App Secret

### 存储安全
- ✅ 敏感数据加密存储（可选）
- ✅ 定期清理过期数据
- ❌ 不要存储明文密码

---

## 关键文件索引

| 功能 | 文件路径 |
|------|----------|
| Token 管理 | `common/auth.js` |
| 全局登录 | `common/global.js` |
| 请求封装 | `common/util/request.js` |
| 环境检测 | `common/auth/core/EnvironmentDetector.js` |
| 飞书登录 | `common/auth/providers/FeishuProvider.js` |
| 登录选择页 | `pages/auth/login-select.vue` |
| OAuth 回调页 | `pages/auth/callback.vue` |
