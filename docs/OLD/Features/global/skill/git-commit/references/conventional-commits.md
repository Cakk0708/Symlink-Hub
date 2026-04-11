# Conventional Commits 规范参考

版本：1.0.0 | 官方文档：https://www.conventionalcommits.org

## 完整格式

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Breaking Changes

在 subject 后加 `!`，或在 footer 写 `BREAKING CHANGE: <描述>`：

```
feat(api)!: remove deprecated /v1/users endpoint

BREAKING CHANGE: /v1/users has been removed. Use /v2/users instead.
```

## Footer 格式

```
Fixes #123
Closes #456
Reviewed-by: Alice <alice@example.com>
Co-authored-by: Bob <bob@example.com>
BREAKING CHANGE: description here
```

## 多行 body 示例

```
fix(payments): prevent race condition in checkout

Introduce a mutex lock around the payment session creation
to prevent duplicate charges when users double-click submit.

The root cause was that two concurrent requests could both
pass the "order not paid" check before either committed.

Fixes #891
```

## Revert 格式

```
revert: feat(auth): add OAuth2 login

This reverts commit abc123def.
Reason: OAuth provider's API is unstable in production.
```