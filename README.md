# AICoach 项目总览

AICoach 是一个基于本地大语言模型（如 Ollama + DeepSeek）构建的 AI 教练 Demo，用于辅助用户进行「科目一」考试的练习与反馈。  
项目采用模块化架构，配合图形 UI 界面、题库系统、AI 模型和语音播报功能，提供沉浸式、交互式的学习体验。

---

## ✅ 已实现功能模块

### 📚 题库模块（Core/QuestionManager + QuestionItem）
- 支持从 JSON 题库加载题目
- 实现题目随机抽取、选项乱序
- 支持公共与个别解析的整合

### 🧠 AI 模型交互（Core/AIInteraction）
- 使用 Ollama 本地模型（DeepSeek）进行反馈生成
- 支持流式输出，逐字传送给 UI
- 自动排除 AI 的“思考”片段，如 `<think>` 标签等

### 🖥️ 图形界面（UI/ChatUI）
- 类微信聊天界面，支持气泡显示、用户输入、滚动查看
- 可配合 AI 流式反馈实时刷新显示内容

### ⚙️ 配置管理（Config/ConfigManager）
- 使用 YAML 格式读取模型地址、名称、开关项等
- 配置是否启用语音、是否记录 AI 失败回答、选项标记等

---

## 📁 项目结构概览

```
AICoachDemo/
├── Main.py                      # 程序入口
├── Source/
│   ├── Core/                    # 题库、AI 模块
│   ├── UI/                      # 图形界面（ChatUI）
│   └── Config/                  # 配置读取
├── Config/
│   └── Settings.yaml            # 配置项（模型、路径、开关等）
├── Data/
│   └── QuestionBank.json        # 科目一题库数据
├── Assets/
│   └── Images/                  # 图片等资源
```

---

## 🚧 后续计划

- ✅ TTS 模块接入（如 ChatTTS）用于语音播报 AI 回复
- ✅ 日志模块记录无法应答的问题
- ✅ 模型接入支持切换（如 Yi、ChatGLM 等）
- ✅ 自动生成错题本、专项练习等拓展功能

---

## 🧠 项目目标

通过本地大模型 + UI 聊天交互，打造一个真实教练般的学习体验平台，让用户更高效掌握考试知识点。

如需启动，请运行：
```bash
python Main.py
```
