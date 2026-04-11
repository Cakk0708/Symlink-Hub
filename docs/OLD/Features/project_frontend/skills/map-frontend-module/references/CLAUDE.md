# 项目规范

## 技术栈
Django 5.x · DRF · PostgreSQL · Celery · Redis

## 开始任何任务前
**必须先阅读 docs/map.md**，了解模块全景和依赖关系。

## 三条铁律
1. 业务逻辑只写 services.py，views 禁止写 if/业务判断
2. 跨模块调用只通过对方 services.py / selectors.py
3. shared/ 禁止引用任何业务模块

## 按需阅读
- 改 API → docs/api-conventions.md
- 改模型 → docs/data-model.md  
- 不熟悉某模块 → docs/modules/{模块名}.md

## 开始任何任务前
必须先阅读 .claude/docs/map.md

## 按需阅读
- 改 API → .claude/docs/api-conventions.md
- 改模型 → .claude/docs/data-model.md
- 不熟悉某模块 → .claude/docs/modules/{模块名}.md