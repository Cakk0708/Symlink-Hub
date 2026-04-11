---
name: project-detail-log
description: PMS 项目操作日志模块专家，负责项目详情页"操作记录"标签页的日志展示与分页加载逻辑。当用户提到"操作记录"、"records.vue"、"项目日志"、"pm/log"、"操作日志"、"历史记录"、"project records"或相关术语时激活此技能。
---

# 项目操作日志模块 (Project Detail Log)

## 模块定位

操作日志模块是 PMS 项目详情页的审计追踪组件，位于 `pagesProject/components/records.vue`，作为项目详情页 `main-article` 区域的第八个标签页（`value: 'records'`）。

该模块提供项目全生命周期的操作历史记录，用于追溯项目变更、了解操作人员、时间及具体变更内容。

---

## 模块职责边界

| 职责 | 包含 | 不包含 |
|------|------|--------|
| **日志展示** | 按时间倒序展示操作记录列表 | 修改日志内容 |
| **分页加载** | 滚动触底自动加载更多日志 | 修改分页大小 |
| **复制功能** | 右键复制日志文本内容 | 复制其他内容 |
| **数据获取** | 调用 `/pm/log` 接口获取日志 | 处理其他接口 |

**边界说明**：
- 本模块是**只读组件**，不负责日志的写入/创建
- 日志的创建由后端在执行项目操作时自动记录
- 不包含日志筛选/搜索功能（当前版本）

---

## 核心数据模型

### 日志条目结构

```javascript
{
  create_time: String,      // 操作时间，格式如 "2024-01-15 14:30:00"
  creator: {                // 操作人信息
    avatar: String,         // 头像 URL
    nickname: String        // 显示名称
  },
  content: String           // 操作内容描述
}
```

### 组件状态

```javascript
data() {
  return {
    recordsList: [],      // 日志列表数组
    recordCount: 0,       // 当前已加载的日志计数（用于 skip 参数）
    isFetched: false,     // 是否已发起首次请求
    noMore: false         // 是否已加载全部数据
  }
}
```

---

## API 接口

### 获取操作日志

**接口地址**: `POST /pm/log`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | String | 是 | 项目 ID |
| skip | Number | 是 | 跳过的记录数（分页偏移量） |
| limit | Number | 是 | 每页返回数量，固定为 20 |

**响应结构**:

```javascript
{
  data: {
    data: {
      list: Array,    // 日志列表
      count: Number   // 本次返回的记录数量
    }
  }
}
```

**接口历史**:
- 旧接口: `web/project?type=10020`（已废弃）
- 新接口: `pm/log`（当前使用）

---

## 权限验证流程

操作日志模块**不涉及独立的权限验证**：

- 日志读取权限继承自项目详情页的整体访问权限
- 只要用户能进入项目详情页，即可查看操作记录
- 不调用 `permission()` 函数进行权限校验

---

## 与其他模块关系

```mermaid
graph TD
    A[项目详情页 main-article] --> B[操作记录标签页]
    B --> C[records.vue 组件]
    C --> D[/pm/log API]
    B --> E[基本信息标签页]
    B --> F[节点管理标签页]
    B --> G[文件管理标签页]
    B --> H[项目结算标签页]
```

| 关联模块 | 关系类型 | 说明 |
|----------|----------|------|
| 项目详情页 (`pagesProject/index/index.vue`) | 父组件 | 通过 `:projectId` prop 传入项目 ID |
| Vuex Store | 数据获取 | 通过 `...mapGetters(['getToken'])` 获取认证 token |
| 全局事件总线 | 事件监听 | 监听 `onReachBottom` 事件实现滚动加载 |

---

## 常见业务场景

### 1. 首次加载日志

**触发时机**: 用户点击"操作记录"标签页

**流程**:
1. 组件 `mounted()` 钩子触发
2. 调用 `getRecordsList()`，`skip=0`
3. 设置 `isFetched=true`
4. 根据返回数量判断 `noMore`

### 2. 滚动加载更多

**触发时机**: 用户滚动至页面底部

**流程**:
1. `uni.$on('onReachBottom')` 事件触发
2. 检查 `isFetched && !noMore` 条件
3. 调用 `getRecordsList()`，使用当前 `recordCount` 作为 `skip`
4. 将新数据 `concat` 到现有列表

### 3. 复制日志内容

**触发时机**: 用户右键点击日志文本

**流程**:
1. `@contextmenu.prevent` 拦截右键菜单
2. 调用 `copyContent(item)`
3. 拼接 `nickname + content`
4. 调用 `uni.setClipboardData()` 复制到剪贴板
5. 显示 toast 提示"已复制"

---

## 技术实现建议 (Django 后端)

如需实现 `/pm/log` 后端接口，建议：

### 1. 模型设计

```python
# models.py
class ProjectLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='logs')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['project', '-create_time']),
        ]
```

### 2. 视图实现

```python
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProjectLogView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get('project_id')
        skip = int(request.data.get('skip', 0))
        limit = int(request.data.get('limit', 20))

        logs = ProjectLog.objects.filter(
            project_id=project_id
        ).select_related(
            'creator'
        ).order_by('-create_time')[skip:skip + limit]

        serializer = ProjectLogSerializer(logs, many=True)

        return Response({
            'data': {
                'list': serializer.data,
                'count': logs.count()
            }
        })
```

### 3. 序列化器

```python
# serializers.py
class ProjectLogSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)

    class Meta:
        model = ProjectLog
        fields = ['create_time', 'creator', 'content']
```

---

## 扩展设计策略

### 短期扩展

1. **日志筛选**: 添加操作人、时间范围、操作类型筛选
2. **关键词搜索**: 支持按日志内容搜索
3. **导出功能**: 导出日志为 Excel/CSV

### 中期扩展

1. **高亮显示**: 特定操作类型（如项目状态变更）使用不同颜色
2. **日志分组**: 按日期分组展示
3. **详情展开**: 某些操作（如字段变更）支持展开查看前后对比

---

## 演进方向 (Future Evolution)

### 1. 实时日志推送

当前采用轮询或手动刷新方式，未来可升级为 WebSocket 实时推送：

```javascript
// 伪代码示例
uni.connectSocket({
  url: `ws://api/pm/log/${projectId}`,
  success: () => {
    uni.onSocketMessage((res) => {
      this.recordsList.unshift(res.data)
    })
  }
})
```

### 2. 结构化日志存储

将日志内容从纯文本升级为结构化 JSON：

```javascript
{
  create_time: "2024-01-15 14:30:00",
  creator: { avatar: "...", nickname: "张三" },
  content: {
    type: "node_status_change",
    summary: "将节点状态从进行中改为已完成",
    details: {
      node_id: 123,
      node_name: "需求分析",
      old_status: 1,
      new_status: 2
    }
  }
}
```

### 3. 联动其他审计模块

与节点评审、文件变更等模块的日志统一管理，形成全局审计中心。

---

## 特有名词索引

当用户提到以下名词时，可快速定位到本模块：

| 名词 | 定位 |
|------|------|
| 操作记录 | 模块名称，详情页标签页 |
| records.vue | 组件文件路径 |
| pm/log | 日志 API 接口 |
| recordCount | 分页偏移量状态 |
| onReachBottom | 滚动加载事件 |
| copyContent | 复制功能方法 |
| creator.nickname | 操作人显示名 |
| avatar | 头像字段 |

---

## 文件路径索引

- **前端组件**: `pagesProject/components/records.vue`
- **父页面**: `pagesProject/index/index.vue:518`（组件导入）、`:638`（标签配置）、`:157`（动态组件渲染）
- **样式文件**: `pagesProject/common/style.scss`（全局样式）

---

## 代码示例

### 复制功能实现

```javascript
copyContent(item) {
  let content = (item.creator && item.creator.nickname
    ? item.creator.nickname + ' '
    : '') + item.content

  uni.setClipboardData({
    data: content,
    success: function () {
      uni.showToast({
        title: '已复制',
        icon: 'none'
      })
    }
  })
}
```

### 分页加载判断

```javascript
this.noMore = res.data.data.list.length < 20
```

**逻辑**: 当返回数量小于请求的 limit（20）时，判定为已无更多数据。

---

## 注意事项

1. **组件销毁**: 必须在 `destroyed()` 钩子中移除事件监听，避免内存泄漏
2. **时间格式**: `create_time` 由后端返回，需确保格式统一
3. **头像处理**: 使用 `mode="widthFix"` 确保图片正确显示
4. **空值处理**: `creator` 可能为 null，需使用 `&&` 短路运算安全访问
5. **列表合并**: 使用 `concat()` 而非 `push()`，避免引用问题
