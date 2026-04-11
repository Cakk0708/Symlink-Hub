# Duolingo 自动化平台

三子项目通过 git submodules 管理：`backend/`（Django）、`frontend/`（PC Vue）、`h5/`（移动 Vue）

## Agent 路由

| 任务类型 | 指派 Agent |
|---------|-----------|
| backend/ 下任何开发 | `backend-python-dev` |
| h5/ 下任何开发 | `h5-frontend-dev` |
| frontend/ 下任何开发 | `frontend-dev` |
| 跨端任务 | 并行启动对应多个 agent |

**规则：收到任务后，先判断目录归属，立即委托对应 agent，不在主会话处理具体代码。**

## 术语说明

涉及任何术语时请参考 `.claude/rules/Terms.md`

## 数据流（参考用）

登录(JWT) → 绑定 Duolingo 账号 → 创建订单(EXP/GEMS/3X_XP/SIGN) → Celery 异步执行 → 记录结果

## 工程目录

- `backend/` — Django REST Framework 后端子工程，由 `backend-python-dev` 驱动
- `frontend/` — Vue3 + Element Plus 管理端子工程，由 `frontend-dev` 驱动  
- `h5/` — Vue3 + Vite H5 移动端子工程，由 `h5-frontend-dev` 驱动

## 开发命令速查
```bash
# 后端（backend/ 目录）
DJANGO_ENVIRONMENT=dev python manage.py runserver 0.0.0.0:8101
DJANGO_ENVIRONMENT=dev celery -A home worker -B --loglevel=info

# 前端（frontend/ 或 h5/ 目录）
npm run dev && npm run build
```

## 缓存规范（强制）

**禁止**直接使用 `redis-py`（即 `import redis`）操作缓存。

所有缓存操作**必须**通过 Django Cache Framework：
```python
# ✅ 正确
from django.core.cache import cache
cache.set('key', value, timeout=300)
cache.get('key')
cache.delete('key')

# ❌ 禁止
import redis
r = redis.Redis(...)
r.set('key', value)
```

Redis 仅作为 Cache Backend 在 settings 中配置：
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
```

> 原因：保持缓存后端可替换性，统一超时管理，避免序列化不一致。