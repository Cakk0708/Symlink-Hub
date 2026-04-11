# 测试

## 当前状态

目前项目**未配置**测试框架。

## 建议配置

### 单元测试

推荐使用 Vitest（Vite 原生测试框架）：

```bash
npm install -D vitest @vue/test-utils
```

配置 `npm run test:unit` 脚本。

### E2E 测试

推荐使用 Cypress 或 Playwright：

```bash
# Cypress
npm install -D cypress

# Playwright
npm install -D @playwright/test
```

配置 `npm run test:e2e` 脚本。

### 代码检查

推荐使用 ESLint：

```bash
npm install -D eslint
```

配置 `npm run lint` 脚本。

## 测试建议

### 单元测试覆盖

- 工具函数（utils）
- Composables 函数
- Pinia stores
- API 接口

### E2E 测试覆盖

- 用户登录流程
- 核心业务流程
- 表单提交
- 页面导航

### 测试命令示例

```bash
# 运行单元测试
npm run test:unit

# 运行 E2E 测试
npm run test:e2e

# 代码检查
npm run lint

# 自动修复
npm run lint:fix
```

## 测试文件组织

```
tests/
├── unit/              # 单元测试
│   ├── utils/
│   ├── composables/
│   └── stores/
└── e2e/               # E2E 测试
    ├── login.spec.js
    ├── customer.spec.js
    └── account.spec.js
```
