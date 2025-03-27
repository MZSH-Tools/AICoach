# AICoach

AICoach 是一个基于本地大语言模型（如 Ollama 的 DeepSeek）构建的 AI 教练 ，旨在辅助用户进行科目一考试练习。该项目实现了题目抽取、用户作答、AI 智能反馈、TTS 语音播报等功能，并支持完整模块化、独立运行与验证。

---

## 🚀 项目目标

- 导入科目一 JSON 题库
- 随机抽题提问用户（支持选项乱序）
- 用户作答后将答案与解析发送给 AI 模型处理
- 使用 AI 给出符合教学话术的反馈
- 支持语音播报、AI 无响应记录、解析开关等功能

---

## 🧱 项目结构

项目目录结构（所有文件夹和文件均采用 PascalCase 命名）：

```bash
AICoachDemo/
├── Main.py                  # 主程序入口
├── Config/
│   ├── ConfigManager.py     # 配置读取模块（支持开关控制功能）
│   └── Settings.yaml        # 配置文件
├── Data/
│   ├── QuestionBank.json    # 科目一题库文件
│   └── UnansweredLog.json   # AI 未能回答的问题记录
├── Core/
│   ├── QuestionManager.py   # 题库加载、抽题、乱序等逻辑
│   ├── AIInteraction.py     # AI Prompt 构建与模型调用
│   └── TTSSpeaker.py        # 语音合成模块
├── UI/
│   ├── ChatUI.py            # 微信风格对话窗口
│   ├── InputBox.py          # 用户输入框
│   └── Animation.py         # 等待 AI 响应时的动画
├── Utils/
│   └── Logger.py            # 日志记录模块（记录未答问题等）
└── Assets/
    └── Images/              # 图片资源
