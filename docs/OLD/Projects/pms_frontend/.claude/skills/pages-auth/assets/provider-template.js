/**
 * 新 Provider 实现模板
 *
 * 使用说明：
 * 1. 复制此文件到 common/auth/providers/{Platform}Provider.js
 * 2. 替换所有 {Platform} 和 {平台} 占位符
 * 3. 实现三个核心方法
 * 4. 在 authProviders.js 中注册
 */

import { getStorage } from '@/common/auth/utils'

class {Platform}Provider extends LoginProvider {
    constructor() {
        super()
        this.id = '{platform}'  // Provider ID，小写
        this.name = '{平台}'      // 显示名称
        this.icon = '{platform}'   // 图标标识
        this.enabled = true         // 是否启用
    }

    /**
     * 检测是否在当前平台容器内
     * @returns {boolean}
     */
    detectEnvironment() {
        const ua = navigator.userAgent || ''

        // 方法一：检查 UserAgent（适用于 H5）
        if (ua.includes('{Platform}标识字符')) {
            return true
        }

        // 方法二：检查全局对象（适用于小程序/SDK）
        if (typeof {Platform全局对象} !== 'undefined') {
            return true
        }

        return false
    }

    /**
     * 发起登录（浏览器环境 OAuth 2.0）
     * @returns {Promise<void>}
     */
    async initiateLogin() {
        // 1. 生成 state 参数（防 CSRF）
        const state = this.generateOAuthState()
        const storage = getStorage()
        storage.setItem('oauth_state', state)
        storage.setItem('oauth_timestamp', Date.now().toString())
        storage.setItem('oauth_provider', this.id)

        // 2. 保存当前页面地址（登录后返回）
        const pages = getCurrentPages()
        if (pages.length > 0) {
            const currentPage = pages[pages.length - 1]
            const route = currentPage.route || 'pages/index/index'
            storage.setItem('oauth_return_url', '/' + route)
        }

        // 3. 构造授权 URL
        const redirectUri = this.getOAuthRedirectUri()
        const authUrl = this.buildAuthUrl(redirectUri, state)

        // 4. 跳转到授权页面
        if (typeof window !== 'undefined') {
            window.location.href = authUrl
        }
    }

    /**
     * 处理 OAuth 回调
     * @param {string} code - 授权码
     * @param {string} state - 状态参数
     * @returns {Promise<TokenData>}
     */
    async handleCallback(code, state) {
        // 1. 验证 state
        if (!this.validateState(state)) {
            throw new Error('安全验证失败')
        }

        // 2. 调用后端接口换取 token
        const tokenData = await this.exchangeCodeForToken(code)

        return tokenData
    }

    /**
     * 生成 OAuth state 参数
     * @returns {string}
     */
    generateOAuthState() {
        return `${this.id}_${Math.random().toString(36).substring(2)}_${Date.now().toString(36)}`
    }

    /**
     * 获取 OAuth 回调地址
     * @returns {string}
     */
    getOAuthRedirectUri() {
        if (typeof window !== 'undefined') {
            return `${window.location.origin}/pages/auth/callback`
        }
        return '/pages/auth/callback'
    }

    /**
     * 构造授权 URL
     * @param {string} redirectUri - 回调地址
     * @param {string} state - 状态参数
     * @returns {string}
     */
    buildAuthUrl(redirectUri, state) {
        // 根据不同平台构造授权 URL
        // 示例：
        return `https://auth.{platform}.com/authorize?` +
            `client_id={APP_ID}` +
            `&response_type=code` +
            `&redirect_uri=${encodeURIComponent(redirectUri)}` +
            `&state=${state}`
    }

    /**
     * 用 code 换取 token
     * @param {string} code - 授权码
     * @returns {Promise<TokenData>}
     */
    async exchangeCodeForToken(code) {
        return new Promise((resolve, reject) => {
            const global = require('@/common/global.js').default
            const config = global.config

            uni.request({
                url: config.path + 'auth/login',
                method: 'POST',
                data: {
                    code: code,
                    provider: this.id  // 关键：指定 provider
                },
                success: (res) => {
                    if (res.statusCode === 200 && res.data.data) {
                        resolve(res.data.data)
                    } else {
                        reject(new Error(res.data.msg || '登录失败'))
                    }
                },
                fail: (err) => {
                    reject(new Error('网络请求失败'))
                }
            })
        })
    }

    /**
     * 验证 state 参数
     * @param {string} state - 回调返回的 state
     * @returns {boolean}
     */
    validateState(state) {
        if (!state) {
            return false
        }

        const storage = getStorage()
        const savedState = storage.getItem('oauth_state')
        const savedProvider = storage.getItem('oauth_provider')
        const timestamp = parseInt(storage.getItem('oauth_timestamp') || '0')
        const now = Date.now()

        // state 不匹配 或 provider 不匹配 或 超过 10 分钟
        if (state !== savedState ||
            savedProvider !== this.id ||
            (now - timestamp) > 10 * 60 * 1000) {
            return false
        }

        // 清除 state
        storage.removeItem('oauth_state')
        storage.removeItem('oauth_provider')
        storage.removeItem('oauth_timestamp')
        return true
    }
}

export default {Platform}Provider
