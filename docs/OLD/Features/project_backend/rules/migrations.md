# Django 迁移文件保护规则

## 规则：禁止修改 migrations 目录

Claude 必须将 Django 应用中的 `migrations` 目录视为 **只读目录**。

严禁进行以下操作：

- 修改已有的 migration 文件
- 删除 migration 文件
- 重命名 migration 文件
- 修改 migration 的依赖关系
- 修改 migration 中的 operations 内容
- 手动编写 migration 文件

## 路径规则

Claude 不得修改以下路径中的任何文件：

*/migrations/*.py

## 允许的操作

Claude 可以：

- 读取 migration 文件以了解数据库结构历史
- 修改 `models.py`
- 建议通过 `python manage.py makemigrations` 生成新的 migration

## 原因

Django 的 migration 文件是数据库结构演进的历史记录。

修改已有 migration 可能导致：

- 数据库迁移失败
- migration 依赖链断裂
- 不同环境（开发 / 测试 / 生产）数据库结构不一致

因此：

**所有已存在的 migration 文件必须被视为不可变历史记录。**
