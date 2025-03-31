# AICoach 项目总览

AICoach 是一个基于本地大语言模型（如 Ollama 的 DeepSeek）构建的 AI 教练 Demo，用于辅助用户进行「科目一」驾驶考试题目的练习与讲解。  
项目以模块化结构开发，支持图形化对话界面、题库抽取、AI 智能反馈、语音播报等功能，旨在打造一个沉浸式、拟人化的练习体验。

---

## ✅ 当前功能进展

已完成模块如下：

- ✅ **图形化 UI 界面（ChatUI）**
  - 类微信风格对话框，支持用户输入、AI 回复、头像气泡展示、滚动区域
- ✅ **题库管理（QuestionManager）**
  - 支持从 JSON 加载题库、随机抽题、乱序选项、动态配置
  - 兼容公共解析与自定义题目解析
- ✅ **题目封装类（QuestionItem）**
  - 用于将单个题目包装成对象，便于统一处理选项、答案、解析等信息
- ✅ **配置系统（ConfigManager）**
  - 使用 YAML 管理开关配置，如是否开启语音、是否乱序等

---

## 🚧 计划开发中的模块

- 🧠 **AI 模型交互模块（AIInteraction）**
  - 负责构建 Prompt、调用本地 LLM 模型（如 DeepSeek）
- 🔊 **语音播报模块（TTSSpeaker）**
  - 使用本地 TTS 工具（如 ChatTTS）播报 AI 回复内容
- 🧾 **日志记录模块（Logger）**
  - 记录 AI 无法回答的问题，便于后续复训或改进

---

## 📁 项目结构（PascalCase 命名规范）

```
AICoachDemo/
├── Main.py                      # 主程序入口
├── Config/
│   ├── ConfigManager.py         # 配置读取模块
│   └── Settings.yaml            # YAML 配置文件
├── Data/
│   ├── QuestionBank.json        # 科目一题库
│   └── UnansweredLog.json       # AI 无法回答的问题记录
├── Core/
│   ├── QuestionManager.py       # 题目调度模块 ✅
│   └── QuestionItem.py          # 单题包装类 ✅
├── UI/
│   └── ChatUI.py                # 图形界面 ✅
├── Utils/
│   └── Logger.py                # 日志记录（待开发）
└── Assets/
    └── Images/                  # 静态资源，如头像、装饰图
```

---

## 🧠 项目愿景

AICoach 项目致力于将传统题库练习转化为 “沉浸式教学对话”，未来将支持：

- 多模型接入（如 DeepSeek、Yi、ChatGLM 等）
- 语音识别与语音回答（端到端体验）
- 错题本生成、考试模式切换、专项训练等

---

如需开发、测试或贡献代码，推荐优先从 `Main.py` 启动入口开始，逐步替换未完成模块。
