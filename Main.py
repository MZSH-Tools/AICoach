from Core.QuestionManager import QuestionManager
from Core.ChatUI import ChatUI

if __name__ == "__main__":
    UI = ChatUI()
    Manager = QuestionManager()

    def OnAIRequested(UserInput, Placeholder):
        # 暂时只从题库中抽一题显示，不处理回答逻辑
        if Manager.NextRandomQuestion():
            UI.DisplayMessageBlocks(Manager.GetMessageBlocks())
        else:
            UI.InsertMessage("ai", "❌ 当前题库中没有题目可用。")

        UI.CompleteReply("(请继续答题)", Placeholder)

    UI.OnAIRequested = OnAIRequested
    UI.Run()
