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

## 路 B：直接给一个能打开的工作台页面

`assets/workbench.html` 是做好的单文件工作台（流体玻璃卡、3D 卡环、队列、详情栏，无任何依赖，浏览器直接打开）。用户要「现成的」就走这条：

1. 复制 `assets/workbench.html` 到用户指定位置（默认 `~/Downloads/`）。
2. 帮用户改文件头部的 `window.WORKBENCH` 配置块：名字、统计卡、队列、卡环项目、详情。只改数据，不动下面的代码。
3. 换主色只改 `accentH` 一个数字。

## 路 C：从零生成个人工作台 Web 应用

1. 读 `references/workbench-prompt.md`。
2. 向用户收集占位符（工作区名、内容平台等，表内有默认示例；用户嫌烦就用示例值直接开工）。
3. 二选一：把填好的提示语交给用户复制走，或直接按提示语在目标目录实现（token 从 `references/design-tokens.md` 取）。

## 边界

- 不改用户字体设置。
- 绿只有三种用法（信号点 / 深绿实底 / 绿字徽章），任何扩展先读 token 表的「禁区」一节。
- 不主动改 Obsidian 主题（theme），只加 snippet；卸载 = 删一个文件。
