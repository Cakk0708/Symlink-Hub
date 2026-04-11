---
name: frontend-layout-map
description: >
  前端任务文件定位技能。凡是用户任务描述中出现 "元素结构（页面名）：模块.子模块.组件"
  格式时，必须立即触发此技能，优先于任何其他操作。适用范围包括但不限于：修改按钮
  文案、调整样式、实现权限控制、修改交互逻辑、新增功能——只要用户用点分路径定位了
  UI 元素，就必须先用此技能解析出对应文件，再执行任务。此技能是所有前端改动的
  前置步骤，不得以"改动不涉及布局"为由跳过。
---

# Frontend Layout Map — 布局地图导航技能

## 目的

当用户用 **点分路径语法** 描述 UI 任务时，本技能帮助 Claude Code 在动手前快速定义前端元素：

1. 解析路径 → 定位对应组件层级
2. 查找布局地图文件，匹配组件路径到实际文件
3. 带上完整上下文再执行任务

---

## 触发语法识别

用户描述中若出现以下任意形式，立即启动本技能：

```
# 完整形式
对 <页面名称>：<模块A>.<模块B>.<模块C> 进行 <任务>

# 元素结构形式
元素结构（对 <页面名称>）：<模块A>.<模块B>.<模块C> 进行 <任务>

# 省略页面名称
对 <模块A>.<模块B> 进行 <任务>

# 多路径
<页面>：<路径1> 和 <路径2> 都需要调整

# 英文混用
<PageName>: <Container>.<Section>.<Component>
```

**示例识别：**
- ✅ `"项目详情页：主容器.节点信息栏.交付物模块"` → 触发
- ✅ `"对首页.导航栏.用户头像做修改"` → 触发
- ✅ `"布局路径：Dashboard.Sidebar.FilterPanel"` → 触发
- ❌ `"修改 ProjectDetail.vue 文件"` → 不触发（直接是文件名）

---

## 执行流程

### Step 1：解析路径

将用户描述中的点分路径拆解为层级数组：

```
"主容器.节点信息栏.交付物模块"
→ [ "主容器", "节点信息栏", "交付物模块" ]
```

如果有页面名称前缀，单独记录：
```
页面: "项目详情页"
路径: [ "主容器", "节点信息栏", "交付物模块" ]
```

### Step 2：功能分端

项目工程可能存在多前端工程情况，需根据用户描述中的页面名称或路径判断属于哪个前端工程。


### Step 3：查找布局地图文件

按以下优先级顺序查找布局地图：

```bash
# 1. 优先查找技能约定位置
find . -name "layouts/*.md" -o -name "layouts/*.json" | head -5

# 2. 查找 rules/ 目录下的布局文档
find ./rules -name "*.md" 2>/dev/null | head -10

# 3. 查找 .claude/ 目录
find ./.claude -name "*.md" 2>/dev/null | head -10

# 4. 查找项目根目录约定文件
ls layout*.md layout*.json LAYOUT*.md 2>/dev/null

# 5. 查找项目根地图文件，从中匹配模块的元素布局文件
ls layout-map.md 2>/dev/null
```

> 如果找到多个候选文件，读取文件名和第一行标题，选择最匹配"页面布局/结构/组件树"语义的那个。

### Step 4：在布局地图中定位

读取布局地图文件后，按层级逐步匹配：

```
层级1：找 "主容器"（或其别名/英文名）
层级2：在 "主容器" 子节点中找 "节点信息栏"
层级3：在 "节点信息栏" 子节点中找 "交付物模块"
```

**模糊匹配规则：**
- 忽略空格差异：`节点信息栏` ≈ `节点 信息栏`
- 忽略括号注释：`交付物（Deliverable）` ≈ `交付物`
- 支持英文对照：如地图中标注 `交付物 / Deliverables`，两种写法都匹配

### Step 5：提取组件信息

布局地图中每个节点应记录（格式见下方"地图格式规范"）：

- `file`：组件文件路径
- `component`：组件名（如有）
- `notes`：额外说明

如果地图中**没有记录文件路径**，执行以下搜索补全：

```bash
# 用模块名搜索组件文件
grep -r "交付物\|Deliverable\|DeliverableModule" \
  --include="*.vue" --include="*.tsx" --include="*.jsx" \
  -l . | head -10
```

### Step 6：输出定位摘要，然后执行任务

在开始修改代码前，先输出一段简短的定位确认：

```
📍 布局路径解析完成
页面：项目详情页
路径：主容器 → 节点信息栏 → 交付物模块
对应文件：src/views/project/components/NodeInfoBar/Deliverables.vue
组件名：DeliverablesModule

现在开始执行任务...
```

如果定位失败（文件不存在或布局地图中没有记录），**不要猜测，先告知用户**：

```
⚠️ 布局路径 "主容器.节点信息栏.交付物模块" 在地图中找到了前两级，
但 "交付物模块" 没有对应的文件记录。

建议：
1. 在布局地图中补充该节点的 file 字段
2. 或直接告诉我文件路径，我来帮你定位
```

---

## 布局地图格式规范

推荐在项目的 `rules/layout-map.md` 或 `.claude/layout-map.md` 中维护布局地图。支持两种格式：

### Markdown 缩进格式（推荐，可读性强）

```markdown
## 项目详情页 (ProjectDetail)

- 主容器 `src/views/project/ProjectDetail.vue`
    - 页面头部 `src/views/project/components/Header/ProjectHeader.vue`
        - 头部左侧 `ProjectHeader.vue > LeftSection`
        - 头部中间 `ProjectHeader.vue > MiddleSection`
        - 头部右侧 `ProjectHeader.vue > RightSection`
    - 流程图区域 `src/views/project/components/FlowChart/`
        - 节点流程图 `FlowChart/NodeCanvas.vue`
        - 节点详情侧边栏 `FlowChart/NodeDetailSidebar.vue`
    - 节点信息栏 `src/views/project/components/NodeInfoBar/`
        - 节点信息 `NodeInfoBar/NodeInfo.vue`
        - 备注 `NodeInfoBar/Remark.vue`
        - 交付物 `NodeInfoBar/Deliverables.vue`
        - 评审项 `NodeInfoBar/ReviewItems.vue`
```

**格式说明：**
- 反引号内是文件路径（相对于项目根目录）
- 若多个子组件在同一文件内，用 `文件名 > 组件名` 标注
- 目录路径以 `/` 结尾表示"查该目录下找对应组件"

### JSON 格式（适合程序化维护）

```json
{
  "pages": {
    "项目详情页": {
      "file": "src/views/project/ProjectDetail.vue",
      "children": {
        "节点信息栏": {
          "file": "src/views/project/components/NodeInfoBar/index.vue",
          "children": {
            "交付物": {
              "file": "src/views/project/components/NodeInfoBar/Deliverables.vue",
              "component": "DeliverablesModule"
            }
          }
        }
      }
    }
  }
}
```
