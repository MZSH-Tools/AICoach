from Source.Config.ConfigManager import ConfigManager
from Source.UI.ChatUI import ChatUI
from Source.Core.QuestionManager import QuestionManager
from Source.Core.AIInteraction import AIInteraction
from Source.Config.ConfigManager import ConfigManager

# 当前状态（答题模式 / AI解析模式）
Mode = "答题"

if __name__ == "__main__":
    UI = ChatUI()
    Manager = QuestionManager()
    AI = AIInteraction()
    Config = ConfigManager()

    # Step 0: 欢迎语 + 第一题
    for line in Config.GetList("欢迎语", []):
        UI.InsertMessage("ai", line)

    if Manager.NextRandomQuestion():
        UI.DisplayMessageBlocks(Manager.GetMessageBlocks())
    else:
        UI.InsertMessage("ai", "❌ 当前题库中没有题目可用。")
        Mode = "结束"

    def OnAIRequested(UserInput, Placeholder):
        global Mode
        UserInput = UserInput.strip()

        if Mode == "答题":
            result = Manager.CheckAnswer(UserInput)
            UI.InsertMessage("ai", result)  # 显示答题结果（正确 / 错误提示等）
            Mode = "解析"
            UI.CompleteReply("(你可以自由提问，或输入“下一题”继续)", Placeholder)
            return

        if Mode == "解析":
            Explanation = Manager.GetExplanation()
            Prompt = AI.BuildPrompt(UserInput, Explanation)

            def OnToken(token):
                UI.AppendTokenToReply(token, Placeholder)
            def OnComplete(token):
                UI.CompleteReply(token, Placeholder)
            AI.QueryStream(Prompt, OnToken, OnComplete)

    UI.OnAIRequested = OnAIRequested
    UI.Run()
