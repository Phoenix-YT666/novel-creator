# 📖 AI小说创作助手 (Novel Creator)

> AI驱动的长篇创作全流程平台，从大纲到出版，AI全程陪伴你的创作之旅。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ 核心功能

### 1. 📋 智能大纲生成
- 多种故事结构：三幕结构 / 英雄之旅 / 四幕 / 网文连载 / 自由风格
- 自动分章规划
- 情节节点设计
- 冲突曲线可视化

### 2. ✍️ AI辅助写作
- 按章节/场景写作
- 多种语气：严肃 / 幽默 / 暗黑 / 轻松 / 悬疑 / 浪漫 / 史诗
- 多视角：第一人称 / 第三人称有限 / 全知 / 第二人称
- 重写 / 扩展 / 润色 / 续写
- 可调创意温度 (0-1)

### 3. 👤 角色工坊
- 角色创建与档案管理
- 性格特征系统
- 角色关系图谱
- 角色弧光规划
- AI 对话生成

### 4. 🌍 世界观构建
- 地理/地图设计
- 势力/阵营系统
- 魔法/科技体系
- 历史时间线
- 文化风俗设定

### 5. 📦 一键导出
- EPUB / PDF / TXT / DOCX / HTML / Markdown
- 自动排版
- 封面设计
- 多平台适配

### 6. 🔍 质量分析
- 节奏分析
- 角色一致性检查
- 情节漏洞检测
- 写作风格统计

---

## 🚀 快速开始

```bash
pip install -r requirements.txt

# 创建新项目
python main.py new "修真纪元" --genre 玄幻 --type web_novel

# 生成大纲
python main.py outline --project "修真纪元" --chapters 100 --style web_serial

# 创建角色
python main.py character create --project "修真纪元" --name 萧尘 --role protagonist

# 开始写作第1章
python main.py write chapter --project "修真纪元" --chapter 1 --length long

# 交互式写作
python main.py interactive --project "修真纪元"
```

---

## 📂 项目结构
```
novel-creator/
├── main.py                  # 主入口
├── novel_creator/
│   ├── __init__.py
│   ├── engine.py           # 创作引擎核心
│   ├── writer.py           # AI写作模块
│   ├── outliner.py         # 大纲系统
│   ├── characters.py       # 角色管理
│   ├── worldbuilding.py    # 世界观构建
│   ├── exporter.py         # 导出模块
│   └── analyzer.py         # 作品分析
├── projects/                # 你的小说项目
├── templates/               # 项目模板
├── exports/                 # 导出的作品
└── requirements.txt
```

## 🛠️ 技术栈
- **AI引擎**: Claude API (Anthropic SDK)
- **文本处理**: Python 标准库 + jieba
- **导出**: ebooklib / python-docx / weasyprint
- **数据**: JSON / YAML 项目文件
- **Web UI**: Gradio (可选)

## 📝 License
MIT © Phoenix-YT666
