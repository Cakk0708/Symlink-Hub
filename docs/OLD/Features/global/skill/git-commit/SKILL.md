---
name: git-commit
description: |
  智能 Git 提交助手。当用户想要提交代码、创建 commit、总结改动并提交、或说"commit"、"帮我提交"、"commit 一下"、"提交代码"时，务必使用此 Skill。
  自动分析 git diff、生成简洁中文 commit message、自动暂存所有变更、按模块自动拆分为多个 commit、提交前展示摘要确认、以及可选的自动 push。
---

# Git Commit Skill

分析当前代码变更，按模块自动拆分为多个 commit，生成简洁的中文提交信息，完成提交流程。

## 工作流程

按以下步骤执行，不要跳过。

### 第一步：检查仓库状态

```bash
git status
git diff --stat
git diff --cached --stat
```

如果没有任何变更（working tree clean），告知用户并终止。

### 第二步：获取详细 diff

```bash
git diff          # 未暂存的变更
git diff --cached # 已暂存的变更
```

重点关注：
- 新增/删除了哪些文件及其所属模块
- 核心逻辑改动（函数、类、接口）
- 配置或依赖变更
- Bug 修复的上下文

### 第三步：按模块自动分组

将所有变更文件按**关注点**（concern）归组。分组依据：

- **目录/模块**：同一功能目录下的文件归为一组（如 `src/auth/`、`src/payment/`）
- **变更性质**：配置文件、依赖文件单独成组（如 `package.json`、`.env`）
- **关联性**：逻辑上强相关的跨目录文件可合并一组

如果所有变更属于同一关注点，则合并为一个 commit。

**分组示例：**
```
分组 1（认证模块）：src/auth/token.ts, src/auth/refresh.ts
分组 2（修复）：src/payment/checkout.ts
分组 3（配置）：package.json, .env.example
```

### 第四步：为每组生成中文 commit message

格式：`<type>(<scope>): <中文描述>`

**type 选择规则：**

| type | 使用场景 |
|------|---------|
| `feat` | 新功能、新接口、新页面 |
| `fix` | 修复 Bug、纠正错误逻辑 |
| `refactor` | 重构（不改变行为） |
| `chore` | 构建脚本、依赖更新、工具配置 |
| `docs` | 文档、注释 |
| `style` | 格式化、空白行（不影响逻辑） |
| `test` | 测试相关 |
| `perf` | 性能优化 |
| `ci` | CI/CD 配置 |
| `revert` | 回滚提交 |

**scope：** 
- 取受影响的模块/目录名，如 `auth`、`api`、`ui`、`db`。可省略。
- 如果没有明确的模块，可以省略 scope。
- 如为 apps 可忽略。
- 如修改点目录为 apps/PM/nodelist/views.py 则 scope 为 `PM/nodelist`。

**中文描述规则：**
- 动词开头，简洁说明做了什么，不超过 20 个字
- 结尾不加句号
- 避免模糊词（"修改"、"更新"），使用具体动词（"新增"、"修复"、"重构"、"删除"）

**示例：**
```
feat(auth): 新增 JWT refresh token 支持
fix(payment): 修复结算页面并发提交导致重复扣款的问题
chore(deps): 升级 axios 至 1.6.0
```

### 第五步：展示完整提交计划供确认

提交前**必须**展示所有分组的提交计划：

```
📋 提交计划（共 N 个 commit）：

Commit 1/3
  文件：src/auth/token.ts, src/auth/refresh.ts
  Message：feat(auth): 新增 JWT refresh token 支持

Commit 2/3
  文件：src/payment/checkout.ts
  Message：fix(payment): 修复结算页面并发提交导致重复扣款的问题

Commit 3/3
  文件：package.json, .env.example
  Message：chore(deps): 升级依赖并更新环境变量示例

确认提交？[是/否/修改]
```

如果用户要求修改某条 message 或调整分组，接收后重新展示计划。

### 第六步：依次执行提交

用户确认后，**按分组顺序**依次执行，每次只暂存该组文件：

```bash
# Commit 1
git add src/auth/token.ts src/auth/refresh.ts
git commit -m "feat(auth): 新增 JWT refresh token 支持"

# Commit 2
git add src/payment/checkout.ts
git commit -m "fix(payment): 修复结算页面并发提交导致重复扣款的问题"

# Commit 3
git add package.json .env.example
git commit -m "chore(deps): 升级依赖并更新环境变量示例"
```

每个 commit 执行后输出结果，全部完成后汇总展示。

### 第七步：询问是否 Push

所有 commit 完成后询问：
> ✅ 全部提交完成（共 N 个）！是否推送到远程？(`git push`)

用户确认后执行 `git push`，展示结果。若推送失败（如需 `--set-upstream`），输出正确命令提示用户手动执行。

---

## 注意事项

- **不要**在用户确认前执行任何 `git add` 或 `git commit`
- 自动 push，当用户确认提交后无需询问直接 push
- 检测到 `package-lock.json`、`yarn.lock` 变更时，单独归为 `chore(deps)` 组，不与业务代码混合
- 检测到 `.DS_Store`、`*.log`、`dist/`、`node_modules/` 等噪声文件时，提醒用户将其加入 `.gitignore`，并询问是否跳过这些文件
- 如果存在 `.git/MERGE_HEAD` 或 `CHERRY_PICK_HEAD`，说明正在合并/cherry-pick，提示用户手动处理后再使用此 Skill
- `git diff` 输出超长（>300 行）时，重点摘要关键变更，不逐行列举

## 参考

Conventional Commits 完整规范见 `references/conventional-commits.md`。