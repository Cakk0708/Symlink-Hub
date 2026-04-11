# 代码规范

## 组件结构

`.vue` 文件按以下顺序编写：

```vue
<template>
  <div>{{ message }}</div>
</template>

<script setup>
import { ref } from 'vue'

const message = ref('Hello')
</script>

<style scoped>
div { color: #333; }
</style>
```

顺序：
1. `<template>` 部分
2. `<script setup>` 部分
3. `<style scoped>` 部分

## 命名规范

- **组件**: `PascalCase` (如 `PageHeader.vue`)
- **变量/函数**: `camelCase`
- **常量**: `UPPER_SNAKE_CASE`
- **事件处理器**: `handle` 前缀 (如 `handleSubmit`)
- **异步数据获取**: `event_` 前缀 (如 `event_get_data`)
- **组合式函数**: `use` 前缀 (如 `useAuth`)

## 导入顺序

```javascript
// 1. Vue 和 Vue 组合式函数
import { ref, onMounted } from 'vue'

// 2. 第三方库 (Vant、axios 等)
import { showToast } from 'vant'

// 3. 内部工具和 API 模块
import request from '@/utils/request'

// 4. 相对导入 (组件)
import PageHeader from '@/components/PageHeader.vue'
```

## 状态管理

- **基础值**: 使用 `ref`
- **对象**: 使用 `reactive`
- **派生状态**: 使用 `computed`

```javascript
const loading = ref(false)
const formData = reactive({ username: '', password: '' })
const isEnabled = computed(() => formData.username.length > 0)
```

## 代码风格

- 使用 2 空格缩进
- 使用单引号
- 语句末尾添加分号
- 组件名使用多词命名
- 避免在模板中使用复杂表达式，提取到 computed 或 methods
