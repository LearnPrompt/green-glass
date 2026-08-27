---
name: green-glass
description: 绿透——纯黑底 + 流体玻璃 + 克制翠绿的个人工作台视觉体系。用户说「绿透」「给 Obsidian 换绿色玻璃皮肤」「装绿透 UI」「obsidian 绿色主题」「生成个人工作台」「做一个绿色玻璃风格的 dashboard」时触发。三条路：A 给 Obsidian vault 装 CSS snippet 皮肤；B 直接给做好的单文件工作台 HTML；C 用内置提示语模板从零生成工作台 Web 应用。
---

# 绿透 green-glass

一套定稿的视觉体系，三种落地方式。所有数值以 `references/design-tokens.md` 为准，不要自己发明。

## 路 A：给 Obsidian 装皮肤

1. 确定 vault 路径（问用户，或从上下文找 `.obsidian` 目录）。
2. 复制 `assets/green-glass.css` 到 `<vault>/.obsidian/snippets/green-glass.css`。
3. 启用：读 `<vault>/.obsidian/appearance.json`，把 `"green-glass"` 加进 `enabledCssSnippets` 数组（保留已有项；文件不存在就建 `{"enabledCssSnippets":["green-glass"]}`）。也可以让用户在 设置 → 外观 → CSS 代码片段 里手动开。
4. 提醒：只在**暗色模式**生效；Obsidian 需要重载（Cmd/Ctrl+R）或重启才能读到新 snippet。
5. 用户想换主色：改 snippet 顶部的 `--accent-h/s/l` 三个值即可，其余取值不动。

## 路 B：装一个连着真数据的工作台页面

`assets/workbench.html` 是单文件工作台（流体玻璃卡、3D 卡环、项目索引、队列、设置四个视图，无依赖，浏览器直接打开）。同目录有 `workbench-data.js` 就显示本机真数据，没有就显示示意数据。

**首次安装（问询式，一次问全）：**

1. 问用户两件事：git 项目根目录（如 `~/projects`）、Obsidian vault 路径（没有就跳过）。
2. 跑采集：`python3 scripts/collect.py --projects <项目目录> --vault <vault> --out <目标目录>`
   —— 扫 git 仓库（分支/未提交/今日提交/久置）+ vault 里的 `- [ ]` 勾选框（新的进待办、老的进积压），生成 `workbench-data.js`。只读不写任何仓库或笔记。
3. 把 `assets/workbench.html` 和生成的 `workbench-data.js` 放同一目录（默认 `~/Downloads/`），打开给用户看。

**待办是混合模式（定案）**：首次安装自动扫用户 vault 的勾选框收纳 todo——有混合信息比没有信息好，别因为怕噪音就留空。收件箱/归档类目录已默认排除，每条带来源文件名让用户自己分辨。在此基础上叠两层可选增强：① 用户有固定任务清单文件时加 `--todo-file <路径>`，该文件的未勾选项直接作为今日队列；② 刷新时 Claude 把当前会话里明确的待办策展补进 `queue.today`。

**「刷新我的工作台」**：重跑第 2 步同参数即可，页面刷新就是新数据。

**从会话记录补待办**：collect.py 只认 vault 勾选框；当前对话里明确的待办事项，刷新时直接编辑 `workbench-data.js` 的 `queue.today` 数组补进去（保持同结构 `{text, badge, tone, time}`），这是 Claude 的活，不是脚本的。

改名字、改主色：文件头 `window.WORKBENCH` 的 `owner/workspace`；主色在页面 设置中心 里点选即可（存浏览器）。

## 路 C：从零生成个人工作台 Web 应用

1. 读 `references/workbench-prompt.md`。
2. 向用户收集占位符（工作区名、内容平台等，表内有默认示例；用户嫌烦就用示例值直接开工）。
3. 二选一：把填好的提示语交给用户复制走，或直接按提示语在目标目录实现（token 从 `references/design-tokens.md` 取）。

## 边界

- 不改用户字体设置。
- 绿只有三种用法（信号点 / 深绿实底 / 绿字徽章），任何扩展先读 token 表的「禁区」一节。
- 不主动改 Obsidian 主题（theme），只加 snippet；卸载 = 删一个文件。
