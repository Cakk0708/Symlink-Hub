# UserHelper 参考

## 位置
`utils/user.py`

## 类方法

### `build_userinfo(user) -> dict`
统一构造 userinfo 字典。

```python
from utils.user import UserHelper

userinfo = UserHelper.build_userinfo(request.user)
# 返回: {
#   'id': user.feishu_id,
#   'open_id': user.open_id,
#   'nickname': user.nickname,
#   'avatar': user.avatar,
#   'mobile': user.mobile,
#   'nickname_pinyin': user.nickname_pinyin,
#   'in_service': user.in_service,
#   'uses': user.uses,
#   'is_leader': user.is_leader,
#   'is_superuser': user.is_superuser,
#   'department': user.department,
# }
```

### `setup_request_userinfo(request, user=None) -> dict`
统一设置 request 对象上的 userinfo 相关属性，并返回 userinfo 字典。

```python
from utils.user import UserHelper

userinfo = UserHelper.setup_request_userinfo(request)
# 或指定 user
userinfo = UserHelper.setup_request_userinfo(request, user=some_user)

# 同时会设置 request.old_user = userinfo
```

## 返回的字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 飞书用户 ID (feishu_id) |
| open_id | str | 飞书 open_id |
| nickname | str | 昵称 |
| avatar | str | 头像 URL |
| mobile | str | 手机号 |
| nickname_pinyin | list | 昵称拼音列表 |
| in_service | bool | 是否在职 |
| uses | int | 使用次数 |
| is_leader | bool | 是否为领导 |
| is_superuser | bool | 是否为超级用户 |
| department | list | 部门信息列表 |
