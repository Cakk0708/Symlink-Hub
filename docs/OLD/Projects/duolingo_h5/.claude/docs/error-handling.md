# 错误处理

## 请求错误处理

### 标准错误处理模式

```javascript
try {
  const response = await request.post('/endpoint', data)
  showToast({ type: 'success', message: '操作成功' })
} catch (error) {
  console.error('请求失败:', error)
  showToast({ type: 'fail', message: error.message || '请求失败' })
} finally {
  loading.value = false
}
```

### 错误类型

1. **网络错误**: 网络连接失败
2. **服务器错误**: 5xx 状态码
3. **客户端错误**: 4xx 状态码
4. **超时错误**: 请求超时
5. **解析错误**: 响应数据格式错误

## 错误提示

使用 Vant 的 Toast 组件显示错误：

```javascript
import { showToast } from 'vant'

// 成功提示
showToast({ type: 'success', message: '操作成功' })

// 失败提示
showToast({ type: 'fail', message: error.message })

// 加载提示
showToast({ type: 'loading', message: '加载中...', duration: 0 })

// 关闭加载
showToast.clear()
```

## 表单验证错误

```javascript
const validateForm = () => {
  if (!formData.username) {
    showToast({ type: 'fail', message: '请输入用户名' })
    return false
  }
  if (!formData.password) {
    showToast({ type: 'fail', message: '请输入密码' })
    return false
  }
  return true
}
```

## 全局错误处理

在请求拦截器中统一处理：

```javascript
// 响应拦截器
response.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Token 过期
          handleTokenRefresh()
          break
        case 403:
          showToast({ type: 'fail', message: '无权访问' })
          break
        case 404:
          showToast({ type: 'fail', message: '请求资源不存在' })
          break
        case 500:
          showToast({ type: 'fail', message: '服务器错误' })
          break
        default:
          showToast({ type: 'fail', message: error.response.data.msg || '请求失败' })
      }
    } else {
      showToast({ type: 'fail', message: '网络错误' })
    }
    return Promise.reject(error)
  }
)
```

## 错误日志

```javascript
const logError = (error, context) => {
  console.error('Error:', {
    message: error.message,
    stack: error.stack,
    context
  })
}
```
