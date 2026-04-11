# FeishuTokenManager 参考

## 位置
`apps/SM/token_manager.py`

## 类方法

### `get_tenant_token() -> str`
获取 tenant_access_token（机器人 token），自动处理缓存和刷新，提前 5 分钟刷新。

```python
from apps.SM.token_manager import FeishuTokenManager

token = FeishuTokenManager.get_tenant_token()
# 返回: "Bearer <tenant_access_token>"
```

### `get_user_token(user) -> str`
获取有效的 user_access_token，自动处理刷新，提前 5 分钟刷新。

```python
from apps.SM.token_manager import FeishuTokenManager

token = FeishuTokenManager.get_user_token(request.user)
# 返回: "<token_type> <access_token>"
```

## 缓存策略

| Token 类型 | 缓存前缀 | 刷新策略 |
|-----------|---------|---------|
| tenant_access_token | `feishu:tenant_access_token:v2` | 提前 5 分钟 |
| app_access_token | `feishu:app_access_token:v2` | 提前 5 分钟 |
| user_access_token | 数据库存储 (`UserFeishuToken`) | 提前 5 分钟 |

## 私有方法

| 方法 | 说明 |
|------|------|
| `_is_token_valid(expires_at)` | 检查 token 是否有效（提前 5 分钟） |
| `_fetch_tenant_token(cache_key)` | 从飞书 API 获取新的 tenant_access_token |
| `_refresh_user_token(token_obj)` | 使用 refresh_token 刷新用户 token |
| `_get_app_token()` | 获取 app_access_token（用于刷新用户 token） |
