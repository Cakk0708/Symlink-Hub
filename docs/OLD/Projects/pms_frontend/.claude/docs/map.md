# PMS 前端项目地图

> 最后更新：2026-03-26

本文档提供项目整体结构的导航地图，帮助快速定位代码位置。

---

## 业务模块全景

### Auth（用户鉴权）
- 模块说明: 负责用户登陆，刷新请求 Token 等业务
- 接口文档: `../pms_backend/.claude/docs/api/sm-auth.md`

### INDEX（项目首页）

#### Project
- 路径: `/`
- 别名: `项目首页/项目列表`
- 模块说明:
- 接口文档: `../pms_backend/.claude/docs/api/pm-project.md`
- 元素布局说明: `.claude/docs/layouts/index.md`

### Detail（项目详情页）
- 路径: `http://localhost:8080/pagesProject/index/index`
- 别名: `项目详情/详情页`
- 模块说明:
- 接口文档: `../pms_backend/.claude/docs/api/pm-project.md`
- 元素布局说明: `.claude/docs/layouts/project-detail.md`
