## 这是一个 Claude 配置文件夹
通过在该文件夹完成项目配置，对目标文件夹创建软连接以实时同步到目标工程文件夹

## 项目配置
- CLAUDE.md
ln -s \
"/Users/Cakk/Library/Mobile Documents/com~apple~CloudDocs/Claude/Projects/pms_backend/CLAUDE.md" \
"/Users/Cakk/Lingyang/pms_backend/CLAUDE.md"

- .claude
ln -s \
"/Users/Cakk/Library/Mobile Documents/com~apple~CloudDocs/Claude/Projects/pms_backend/.claude" \
"/Users/Cakk/Lingyang/pms_backend/.claude"

- .vscode
ln -s \
"/Users/Cakk/Library/Mobile Documents/com~apple~CloudDocs/Claude/Projects/pms_backend/.vscode" \
"/Users/Cakk/Lingyang/pms_backend/.vscode"

- .mcp.json
ln -s \
"/Users/Cakk/Library/Mobile Documents/com~apple~CloudDocs/Claude/Projects/pms_backend/.mcp.json" \
"/Users/Cakk/Lingyang/pms_backend/.mcp.json"

- skills
ln -s \
"/Users/Cakk/Library/Mobile Documents/com~apple~CloudDocs/Claude/skills" \
"/Users/Cakk/Lingyang/pms_backend/.claude/skills"

- rules
ln -s \
"/Users/Cakk/Library/Mobile Documents/com~apple~CloudDocs/Claude/Features/global/skill" \
"/Users/Cakk/.claude/skills"

## 使用特性
1. 可以直接在软连接目标中编辑，同时也会编辑主文件