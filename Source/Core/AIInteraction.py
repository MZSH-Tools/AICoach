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

    @staticmethod
    def BuildPrompt(UserInput="",  Explanations=None) -> str:
        PromptText = "你是一个严肃认真的驾校教练，正在帮助学生练习科目一考试，我会为你提供问题解析库，请根据用户输入找到相关问题的解析并回答给用户。"
        PromptText += "如果用户想要开始做下一道题，请你回复'下一道题'。"
        PromptText += "如果用户问的问题没有在解析库找到相关解析，请你回复'没有找到'。"
        PromptText += f"用户输入是:{UserInput}。"
        PromptText += f"解析库是{Explanations}。"
        return PromptText

    def QueryStream(self, PromptText: str, OnTokenCallback=None) -> str:
        Payload = {
            "model": self.ModelName,
            "prompt": PromptText,
            "stream": True
        }
        CollectedResponse = ""
        try:
            ExcludeThink = self.Config.GetBool("排除思考", "true")
            Response = requests.post(self.ModelURL, json=Payload, stream=True)
            Response.raise_for_status()
            for Line in Response.iter_lines():
                if not Line:
                    continue
                try:
                    JsonLine = json.loads(Line.decode("utf-8"))
                    Token = JsonLine.get("response", "")
                    if Token == "</think>":
                        if ExcludeThink:
                            ExcludeThink = False
                            continue
                    if ExcludeThink:
                        continue
                    if OnTokenCallback:
                        OnTokenCallback(Token)
                    CollectedResponse += Token
                except Exception as Error:
                    continue
        except Exception as Error:
            return f"[请求出错] {str(Error)}"
        return CollectedResponse

if __name__ == "__main__":
    def PrintToken(Token):
        print(Token, end="", flush=True)

    AI = AIInteraction()
    Manager = QuestionManager()
    Explanations = Manager.GetExplanation()
    AI.QueryStream(AI.BuildPrompt("为什么A是错误答案", Explanations), PrintToken)