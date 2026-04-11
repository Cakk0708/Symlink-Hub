# 环境配置

## 环境类型

项目支持多种环境配置，通过 `ENV_TYPE` 环境变量控制。

| 环境变量 | 说明 |
|----------|------|
| h5-dev | 开发环境（通用） |
| h5-dev_fwt | 开发环境（fwt 本地） |
| h5-dev_fkq | 开发环境（fkq 本地） |
| h5-test | 测试环境 |
| h5-prod | 生产环境 |

---

## 配置文件

### env.js
位置：`/env.js`

```javascript
// OAuth API 基础 URL
const oauthTestBaseUrl = 'https://pms-test.lingyang-electronics.com/api'
const oauthProdBaseUrl = 'https://pms.lingyang-electronics.com/api'

// 环境配置
const envConfig = {
	'h5-dev': {
		appid: 'cli_a577f7d3b8881013',
		baseUrl: 'http://192.168.31.10:8001/',
		oauthBaseUrl: oauthTestBaseUrl,
		tokenKey: 'betaToken',
		userKey: 'betaUserInfo',
		userListKey: 'betaUserList'
	},
	'h5-dev_fwt': {
		appid: 'cli_a577f7d3b8881013',
		baseUrl: 'http://192.168.31.134:8006/',
		oauthBaseUrl: oauthTestBaseUrl,
		tokenKey: 'betaToken',
		userKey: 'betaUserInfo',
		userListKey: 'betaUserList'
	},
	'h5-dev_fkq': {
		appid: 'cli_a577f7d3b8881013',
		baseUrl: 'http://192.168.31.88:8001/',
		oauthBaseUrl: oauthTestBaseUrl,
		tokenKey: 'betaToken',
		userKey: 'betaUserInfo',
		userListKey: 'betaUserList'
	},
	'h5-test': {
		appid: 'cli_a577f7d3b8881013',
		baseUrl: 'https://pms-test.lingyang-electronics.com/api/',
		oauthBaseUrl: oauthTestBaseUrl,
		tokenKey: 'betaToken',
		userKey: 'betaUserInfo',
		userListKey: 'betaUserList'
	},
	'h5-prod': {
		appid: 'cli_a5fa8b3bf6fb900b',
		baseUrl: 'https://pms.lingyang-electronics.com/api/',
		oauthBaseUrl: oauthProdBaseUrl,
		tokenKey: 'betaToken',
		userKey: 'betaUserInfo',
		userListKey: 'betaUserList'
	}
}
```

---

## 配置说明

### appid
飞书应用的 AppID，不同环境使用不同的应用：
- 开发/测试环境：`cli_a577f7d3b8881013`
- 生产环境：`cli_a5fa8b3bf6fb900b`

### baseUrl
API 请求的基础 URL：
- 开发环境：本地 IP 地址（用于本地开发调试）
- 测试环境：`https://pms-test.lingyang-electronics.com/api/`
- 生产环境：`https://pms.lingyang-electronics.com/api/`

### oauthBaseUrl
OAuth 认证 API 的基础 URL：
- 开发/测试环境：`https://pms-test.lingyang-electronics.com/api`
- 生产环境：`https://pms.lingyang-electronics.com/api`

### tokenKey
Token 存储的键名（固定为 `betaToken`）

### userKey
用户信息存储的键名（固定为 `betaUserInfo`）

### userListKey
用户列表存储的键名（固定为 `betaUserList`）

---

## 环境切换

### 开发环境
```bash
# 通用开发环境
ENV_TYPE=h5-dev

# fwt 本地开发
ENV_TYPE=h5-dev_fwt

# fkq 本地开发
ENV_TYPE=h5-dev_fkq
```

### 测试环境
```bash
ENV_TYPE=h5-test
```

### 生产环境
```bash
ENV_TYPE=h5-prod
```

---

## 构建配置

### manifest.json
构建时根据 `ENV_TYPE` 动态修改配置：

```javascript
// 构建脚本读取 ENV_TYPE
// 修改 manifest.json 中的相关配置
// 执行构建
```

### vue.config.js
```javascript
module.exports = {
	// 环境变量
	env: {
		ENV_TYPE: process.env.ENV_TYPE || 'h5-dev'
	}
}
```

---

## 环境检测

### 在代码中使用
```javascript
import envConfig from '../env.js'

const { appid, baseUrl, oauthBaseUrl } = envConfig[process.env.ENV_TYPE]

// 根据环境执行不同逻辑
if (process.env.ENV_TYPE === 'h5-prod') {
	// 生产环境逻辑
} else {
	// 开发/测试环境逻辑
}
```

### 环境判断工具函数
```javascript
function isProd() {
	return process.env.ENV_TYPE === 'h5-prod'
}

function isTest() {
	return process.env.ENV_TYPE === 'h5-test'
}

function isDev() {
	return process.env.ENV_TYPE?.startsWith('h5-dev')
}
```

---

## URL 配置

### API 请求 URL
```javascript
// 完整 URL = baseUrl + 接口路径
const fullUrl = baseUrl + 'pm/project/list'
// 例如：http://192.168.31.10:8001/pm/project/list
```

### OAuth 授权 URL
```javascript
// 授权 URL = oauthBaseUrl + 授权路径
const authUrl = oauthBaseUrl + '/sm/auth/login'
// 例如：https://pms-test.lingyang-electronics.com/api/sm/auth/login
```

### 回调 URL
```javascript
// H5 环境
const redirectUri = `${window.location.origin}/pages/auth/callback`

// 小程序环境
const redirectUri = baseUrl
```

---

## 开发调试

### 本地开发配置
1. 确认本地后端服务启动
2. 设置 `ENV_TYPE=h5-dev`（或对应的本地环境）
3. 配置正确的本地 IP 地址

### 调试技巧
```javascript
// 查看当前环境
console.log('当前环境:', process.env.ENV_TYPE)

// 查看配置
import global from '@/common/global'
console.log('API 地址:', global.config.path)
console.log('AppID:', global.config.appid)
```

---

## 生产部署

### 部署前检查
- [ ] 确认 `ENV_TYPE=h5-prod`
- [ ] 确认使用生产环境 AppID
- [ ] 确认 API 地址正确
- [ ] 确认 OAuth 配置正确

### 构建命令
```bash
# H5 生产构建
npm run build:h5 -- --mode production

# 微信小程序生产构建
npm run build:mp-weixin -- --mode production
```

---

## 常见问题

### 问题1：跨域错误
**原因**：开发环境本地 IP 配置错误
**解决**：检查 `env.js` 中的 `baseUrl` 是否为正确的本地 IP

### 问题2：OAuth 授权失败
**原因**：AppID 或环境不匹配
**解决**：
- 检查 AppID 是否正确
- 确认飞书应用配置的回调地址

### 问题3：Token 无效
**原因**：测试/生产环境 Token 混用
**解决**：清除本地 Token，重新登录

### 问题4：接口 404
**原因**：baseUrl 配置错误
**解决**：检查 `env.js` 配置，确认 API 地址正确

---

## 环境对比

| 配置项 | 开发环境 | 测试环境 | 生产环境 |
|--------|----------|----------|----------|
| AppID | cli_a577f7d3b8881013 | cli_a577f7d3b8881013 | cli_a5fa8b3bf6fb900b |
| API 地址 | 本地 IP | pms-test | pms |
| OAuth | 测试环境 | 测试环境 | 生产环境 |
| 用途 | 本地开发 | 测试验证 | 正式使用 |

---

## 配置文件位置索引

| 文件 | 路径 | 说明 |
|------|------|------|
| 环境配置 | `/env.js` | 各环境配置 |
| 全局配置 | `/common/global.js` | 读取环境配置 |
| Token 管理 | `/common/auth.js` | 使用配置中的键名 |
| 请求封装 | `/common/util/request.js` | 使用配置中的 baseUrl |
