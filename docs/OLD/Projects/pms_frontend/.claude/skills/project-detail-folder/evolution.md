# PMS 文件管理模块 - 演进路线图

## 当前状态 (v1.0.0)

### 已实现功能
- ✅ 文件夹树形结构展示
- ✅ 交付物列表展示
- ✅ 创建者头像+昵称展示
- ✅ 文件状态展示（正常/冻结）
- ✅ 树形展开/收起交互
- ✅ 接口数据结构转换
- ✅ 删除文件事件监听
- ✅ 添加文件事件监听

### 已知技术债务
- ⚠️ 点击跳转功能已注释（待重新实现）
- ⚠️ 文件上传功能未实现
- ⚠️ 文件预览功能缺失
- ⚠️ 缺少文件操作权限验证

## 短期优化 (v1.1.0 - 1个月内)

### 功能完善

#### 1. 点击跳转功能重新实现
```javascript
// 目标: 实现文件点击跳转逻辑
async clickGotoDoc(item) {
  // 1. 根据文件类别判断跳转方式
  switch(item.fileCategory) {
    case 'document':
    case 'video':
      // 调用飞书文档预览接口
      await this.openFeishuPreview(item)
      break
    case 'url':
      // 直接跳转
      window.open(item.url, '_blank')
      break
    case 'image':
      // 图片预览弹窗
      this.openImagePreview(item)
      break
  }
}

async openFeishuPreview(item) {
  // 调用新接口获取预览链接
  const res = await this.$util.request({
    url: `pm/deliverable/${item.id}/preview`,
    method: 'GET'
  })

  if (res.statusCode === 200) {
    const previewUrl = res.data.data.url
    window.open(`https://applink.feishu.cn/client/web_url/open?mode=window&height=700&width=900&url=${previewUrl}`)
  }
}
```

#### 2. 文件上传功能
```vue
<template>
  <view class="upload-area">
    <uni-file-picker
      :value="fileList"
      file-extname="pdf,doc,docx,xls,xlsx,jpg,png"
      :limit="9"
      @select="onFileSelect"
      @progress="onFileProgress"
      @success="onFileSuccess"
      @fail="onFileFail"
    />
  </view>
</template>

<script>
methods: {
  async onFileSelect(e) {
    const files = e.tempFiles
    for (let file of files) {
      await this.uploadFile(file)
    }
  },

  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file.file)
    formData.append('folder_id', this.currentFolderId)

    const res = await this.$util.uploadFile({
      url: `pm/project/${this.projectId}/deliverable`,
      filePath: file.path,
      name: 'file',
      formData: {
        folder_id: this.currentFolderId,
        file_category: this.getFileCategory(file.name)
      }
    })

    if (res.statusCode === 200) {
      uni.showToast({ title: '上传成功', icon: 'success' })
      // 刷新列表
      this.getFolderData()
    }
  }
}
</script>
```

#### 3. 文件状态操作
```javascript
// 冻结/解冻功能
async toggleFreeze(item, reason = '') {
  const newState = item.state === 1 ? 2 : 1

  const res = await this.$util.request({
    url: `pm/deliverable/${item.id}/state`,
    method: 'PATCH',
    data: {
      state: newState,
      reason: reason
    }
  })

  if (res.statusCode === 200) {
    item.state = newState
    uni.showToast({
      title: newState === 2 ? '已冻结' : '已解冻',
      icon: 'success'
    })
  }
}
```

### 用户体验优化

#### 1. 加载状态
```vue
<template>
  <view class="delivery-flie">
    <uni-load-more
      v-if="loading"
      status="loading"
      :content-text="{
        contentdown: '上拉显示更多',
        contentrefresh: '加载中',
        contentnomore: '没有更多数据了'
      }"
    />
    <treeNode v-else ... />
  </view>
</template>
```

#### 2. 空状态提示
```vue
<template>
  <view v-if="folderData.length === 0" class="empty-state">
    <image src="/static/empty-folder.png" />
    <text>暂无文件</text>
  </view>
</template>

<style lang="scss" scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #B7C4C5;

  image {
    width: 120px;
    height: 120px;
    margin-bottom: 16px;
  }
}
</style>
```

#### 3. 错误处理
```javascript
async getFolderData() {
  try {
    this.loading = true
    const res = await this.$util.request({
      url: `pm/project/${this.projectId}/folder`,
      method: 'GET'
    })

    if (res.statusCode === 200 && res.data.msg === 'success') {
      this.folderData = this.transformToTreeStructure(res.data.data.items || [])
      // ...
    } else {
      throw new Error(res.data.msg || '获取文件列表失败')
    }
  } catch (error) {
    uni.showToast({
      title: error.message || '网络错误',
      icon: 'none'
    })
    console.error('getFolderData error:', error)
  } finally {
    this.loading = false
  }
}
```

## 中期规划 (v2.0.0 - 3-6个月)

### 文件版本管理

#### 1. 版本历史
```typescript
interface DeliverableVersion {
  id: number;
  deliverableId: number;
  version: string;
  fileUrl: string;
  createdAt: string;
  createdBy: Creator;
  changeLog: string;
}

// 组件
<version-history
  :deliverable-id="currentItem.id"
  @restore="handleVersionRestore"
/>
```

#### 2. 版本对比
```javascript
// 目标: 支持两个版本间的差异对比
async compareVersions(version1, version2) {
  const res = await this.$util.request({
    url: `pm/deliverable/${this.currentItem.id}/versions/compare`,
    method: 'POST',
    data: {
      version1: version1,
      version2: version2
    }
  })

  // 显示差异对比弹窗
  this.showVersionDiffDialog(res.data.data)
}
```

### 文件夹嵌套

#### 1. 多层级文件夹
```typescript
interface FolderNode {
  id: number;
  name: string;
  parentId: number | null;
  children: FolderNode[];
  deliverables: Deliverable[];
  level: number;  // 层级深度
}

// 递归渲染
<folder-item
  v-for="folder in folderTree"
  :key="folder.id"
  :folder="folder"
  :level="0"
/>
```

#### 2. 面包屑导航
```vue
<template>
  <view class="breadcrumb">
    <view
      v-for="(item, index) in breadcrumbList"
      :key="item.id"
      class="breadcrumb-item"
    >
      <text @click="navigateToFolder(item)">{{ item.name }}</text>
      <text v-if="index < breadcrumbList.length - 1"> / </text>
    </view>
  </view>
</template>
```

### 文件搜索

#### 1. 搜索功能
```vue
<template>
  <view class="search-bar">
    <uni-search-bar
      v-model="searchKeyword"
      placeholder="搜索文件名"
      :focus="false"
      :show-action="!!searchKeyword"
      @confirm="handleSearch"
      @cancel="handleSearchCancel"
    />
  </view>
</template>

<script>
methods: {
  handleSearch() {
    if (!this.searchKeyword.trim()) {
      this.filteredData = this.folderData
      return
    }

    this.filteredData = this.filterFolderTree(
      this.folderData,
      this.searchKeyword
    )
  },

  filterFolderTree(nodes, keyword) {
    return nodes.reduce((result, node) => {
      // 匹配文件夹名
      const matchFolder = node.name.includes(keyword)
      // 匹配文件
      const matchedFiles = node.file.filter(f => f.name.includes(keyword))

      if (matchFolder || matchedFiles.length > 0) {
        result.push({
          ...node,
          file: matchFolder ? node.file : matchedFiles
        })
      }

      return result
    }, [])
  }
}
</script>
```

#### 2. 高亮显示
```vue
<template>
  <text class="file-name">
    <template v-for="(part, index) in highlightParts(item.name, searchKeyword)">
      <text
        v-if="part.isMatch"
        :key="index"
        class="highlight"
      >{{ part.text }}</text>
      <text v-else :key="index">{{ part.text }}</text>
    </template>
  </text>
</template>

<script>
methods: {
  highlightParts(text, keyword) {
    if (!keyword) return [{ text, isMatch: false }]

    const parts = []
    const regex = new RegExp(`(${keyword})`, 'gi')
    let lastIndex = 0
    let match

    while ((match = regex.exec(text)) !== null) {
      // 匹配前的文本
      if (match.index > lastIndex) {
        parts.push({
          text: text.slice(lastIndex, match.index),
          isMatch: false
        })
      }

      // 匹配的文本
      parts.push({
        text: match[1],
        isMatch: true
      })

      lastIndex = regex.lastIndex
    }

    // 剩余文本
    if (lastIndex < text.length) {
      parts.push({
        text: text.slice(lastIndex),
        isMatch: false
      })
    }

    return parts
  }
}
</script>

<style lang="scss" scoped>
.highlight {
  color: #3A75FF;
  font-weight: bold;
}
</style>
```

## 长期愿景 (v3.0.0 - 6-12个月)

### 文件在线编辑

#### 1. 集成在线编辑器
```javascript
// 目标: 支持 Word/Excel/PPT 在线编辑
async openOnlineEditor(item) {
  const res = await this.$util.request({
    url: `pm/deliverable/${item.id}/edit_url`,
    method: 'GET'
  })

  if (res.statusCode === 200) {
    // 打开飞书文档/表格/演示编辑器
    window.open(res.data.data.edit_url, '_blank')
  }
}
```

#### 2. 自动保存
```javascript
// 监听编辑器保存事件
window.addEventListener('message', (event) => {
  if (event.data.type === 'DOCUMENT_SAVED') {
    this.refreshFileVersionList()
  }
})
```

### 文件协作评论

#### 1. 评论功能
```typescript
interface FileComment {
  id: number;
  deliverableId: number;
  userId: number;
  content: string;
  createdAt: string;
  replies: FileComment[];
}

// 组件
<file-comments
  :deliverable-id="currentItem.id"
  @add="handleAddComment"
  @delete="handleDeleteComment"
/>
```

#### 2. @提人功能
```vue
<template>
  <view class="comment-input">
    <textarea
      v-model="commentText"
      placeholder="输入评论，@提人通知"
      @input="handleInput"
    />
    <user-mention
      v-if="showMention"
      :keyword="mentionKeyword"
      @select="handleSelectUser"
    />
  </view>
</template>
```

### AI 文件分类

#### 1. 智能分类
```javascript
// 目标: 根据文件内容自动分类
async autoClassifyFile(fileId) {
  const res = await this.$util.request({
    url: `pm/deliverable/${fileId}/classify`,
    method: 'POST'
  })

  if (res.statusCode === 200) {
    const suggestedCategory = res.data.data.category
    const suggestedFolder = res.data.data.folder

    uni.showModal({
      title: 'AI 建议',
      content: `建议将文件归类为: ${suggestedCategory}，移动到: ${suggestedFolder}`,
      success: (res) => {
        if (res.confirm) {
          this.applyAISuggestion(fileId, suggestedCategory, suggestedFolder)
        }
      }
    })
  }
}
```

#### 2. 重复文件检测
```javascript
// 目标: 检测项目中的重复文件
async detectDuplicates() {
  const res = await this.$util.request({
    url: `pm/project/${this.projectId}/deliverables/duplicates`,
    method: 'GET'
  })

  if (res.statusCode === 200 && res.data.data.length > 0) {
    this.showDuplicateDialog(res.data.data)
  }
}
```

## 迁移计划

### 阶段 1: 准备阶段 (2周)
- [ ] 分析现有代码结构
- [ ] 确定后端接口需求
- [ ] 设计数据模型
- [ ] 制定测试计划

### 阶段 2: 功能完善 (1个月)
- [ ] 实现点击跳转功能
- [ ] 实现文件上传功能
- [ ] 实现状态操作功能
- [ ] 添加加载和错误状态
- [ ] 编写单元测试

### 阶段 3: 体验优化 (1个月)
- [ ] 添加文件搜索功能
- [ ] 实现文件夹嵌套
- [ ] 添加面包屑导航
- [ ] 优化头像加载
- [ ] 性能优化

### 阶段 4: 高级功能 (2个月)
- [ ] 文件版本管理
- [ ] 文件在线编辑
- [ ] 文件协作评论
- [ ] AI 文件分类
- [ ] 集成测试

## 成功指标

### 性能指标
- [ ] 文件列表加载时间 < 1s
- [ ] 树形展开/收起响应时间 < 100ms
- [ ] 文件上传速度 > 1MB/s

### 质量指标
- [ ] 单元测试覆盖率 > 80%
- [ ] E2E 测试场景 > 20
- [ ] Bug 率 < 1%

### 用户体验指标
- [ ] 文件搜索准确率 > 95%
- [ ] 文件上传成功率 > 99%
- [ ] 用户满意度 > 4.5/5
