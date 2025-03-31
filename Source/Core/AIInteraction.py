import requests
import json
from Source.Core.QuestionManager import QuestionManager
from Source.Config.ConfigManager import ConfigManager

# AIInteraction 模块负责构建 Prompt 并调用 Ollama 模型生成教学反馈（支持流式输出）
class AIInteraction:
    def __init__(self):
        self.Config = ConfigManager()
        self.ModelURL = self.Config.GetString("模型地址", "http://localhost:11434/api/generate")
        self.ModelName = self.Config.GetString("模型名称", "deepseek-r1:14b")

    def BuildPrompt(self, QuestionBlocks, UserAnswer, CorrectAnswers, Explanations) -> str:
        PromptText = "你是一位温和且专业的驾校教练，正在帮助学生练习科目一考试。\n"
        PromptText += "请根据题目、用户回答、正确答案以及解析，为用户提供清晰、亲切的反馈。\n"
        PromptText += "---\n题目内容：\n"
        for Block in QuestionBlocks:
            PromptText += f"{Block}\n"
        PromptText += f"\n用户回答：{UserAnswer}\n"
        PromptText += f"正确答案：{', '.join(CorrectAnswers)}\n"
        PromptText += "\n解析内容：\n"
        for Line in Explanations:
            PromptText += f"{Line}\n"
        PromptText += "---\n请用第一人称，向学生说明他的答案是否正确，如果错误，指出错在哪里，并耐心解释。"
        return PromptText

    def QueryStream(self, PromptText: str, OnTokenCallback=None) -> str:
        Payload = {
            "model": self.ModelName,
            "prompt": PromptText,
            "stream": True
        }
        CollectedResponse = ""
        try:
            Response = requests.post(self.ModelURL, json=Payload, stream=True)
            Response.raise_for_status()
            for Line in Response.iter_lines():
                if not Line:
                    continue
                try:
                    JsonLine = json.loads(Line.decode("utf-8"))
                    Token = JsonLine.get("response", "")
                    # 过滤典型思考内容
                    if Token.strip().lower() in ["thinking...", "let me think", "嗯", "让我想想"]:
                        continue
                    if OnTokenCallback:
                        OnTokenCallback(Token)
                    CollectedResponse += Token
                except Exception as Error:
                    continue
        except Exception as Error:
            return f"[请求出错] {str(Error)}"
        return CollectedResponse

    def GetFeedback(self, UserAnswer: str, OnTokenCallback=None) -> str:
        Manager = QuestionManager()
        QuestionBlocks = Manager.GetMessageBlocks()
        CorrectAnswers = Manager.GetCorrectAnswers()
        Explanations = Manager.GetExplanation()

        PromptText = self.BuildPrompt(QuestionBlocks, UserAnswer, CorrectAnswers, Explanations)
        return self.QueryStream(PromptText, OnTokenCallback)


if __name__ == "__main__":
    def PrintToken(Token):
        print(Token, end="", flush=True)

    AI = AIInteraction()
    AI.GetFeedback("A", PrintToken)