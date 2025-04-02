# 🤖 AICoach 项目总览

AICoach 是一个基于本地大语言模型（如 Ollama + DeepSeek）构建的 AI 教练 Demo，用于辅助用户进行「科目一」考试的练习与反馈。  
项目采用模块化架构，结合图形界面、题库系统、AI 交互与语音播报功能，提供沉浸式、交互式的学习体验。

---

## ✅ 项目功能模块

### 📚 题库模块（`Source/Core/QuestionManager.py` + `QuestionItem.py`）
- 从 JSON 加载题库
- 支持题目随机抽取与选项乱序
- 正确与错误解析内容整合处理

### 🧠 AI 模型交互（`Source/Core/AIInteraction.py`）
- 基于本地 Ollama 模型（默认 DeepSeek）
- 支持流式输出，并逐字传送至 UI
- 自动排除 `<think>` 等无效片段

### 🖥️ 图形界面 UI（`Source/UI/ChatUI.py`）
- 类微信聊天界面，支持用户输入 / AI 回复 / 滚动显示
- 配合流式反馈实时刷新显示内容

### ⚙️ 配置管理（`Config/Settings.yaml`）
- YAML 格式配置模型、路径、开关选项
- 欢迎语、语音功能、错误记录等设置项集中管理

---

## 📁 项目结构概览

```
AICoach/
├── Main.py                      # 程序入口
├── Source/
│   ├── Core/                    # 题库与 AI 模块
│   ├── UI/                      # 图形界面模块
│   └── Config/                  # 配置读取模块
├── Config/
│   └── Settings.yaml            # 主配置文件（可改为 Settings_Optimized.yaml）
├── Data/
│   └── QuestionBank.json        # 科目一题库数据
├── Assets/
│   └── Images/                  # 图片等资源
```

---

## 🔊 使用说明

1. **安装依赖：**（需安装 Python3 + requests + stream 库）
2. **启动程序：** 运行 `python Main.py`
3. **模型启动：** 请先启动 Ollama 服务，并加载 DeepSeek 模型
4. **配置调整：** 参考 `Settings.yaml` 修改模型地址、语音等设置项

---

## 🔧 后续开发计划

- ✅ 接入 ChatTTS 实现 AI 语音播报
