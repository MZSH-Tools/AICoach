from Source.Config.ConfigManager import ConfigManager
from Source.UI.ChatUI import ChatUI
from Source.Core.QuestionManager import QuestionManager
from Source.Core.AIInteraction import AIInteraction
import threading

Mode = "待机"

def TryNextQuestion(Placeholder):
    global Mode
    if Manager.NextRandomQuestion():
        UI.AppendMessageReply(Manager.GetMessageBlocks(), Placeholder)
        UI.AppendTextToReply("请输入正确答案。", Placeholder)
        UI.CompleteReply()
        Mode = "答题"
    else:
        UI.AppendTextToReply("❌ 当前题库中没有题目可用。", Placeholder)
        Mode = "结束"

def OnAIRequested(UserInput, Placeholder):
    global Mode

    def Handle():
        global Mode
        match Mode:
            case "待机":
                TryNextQuestion(Placeholder)
            case "答题":
                Done, Result = Manager.CheckAnswer(UserInput)
                UI.AppendMessageReply(Result, Placeholder)
                if Done:
                    Mode = "解析"
                    UI.AppendTextToReply("您可以询问我任何题目相关问题，或者说开启下一道题。", Placeholder)
                UI.CompleteReply()
            case "解析":
                Explanation = Manager.GetExplanation()
                Prompt = AI.BuildPrompt(UserInput, Explanation)

                def OnToken(Token):
                    UI.AppendTokenToReply(Token, Placeholder)

                def OnComplete(FinalText):
                    match FinalText:
                        case "下一道题":
                            UI.ClearPlaceholder(Placeholder)
                            TryNextQuestion(Placeholder)
                        case "没有找到":
                            UI.ClearPlaceholder(Placeholder)
                            UI.AppendTextToReply("抱歉无法解析，改问题将上传至工作人员后台，请问你还有其他问题吗", Placeholder)
                    UI.CompleteReply()
                    print(FinalText)
                    print(len(FinalText))

                AI.QueryStream(Prompt, OnTokenCallback=OnToken, OnComplete=OnComplete)

    threading.Thread(target=Handle).start()

def PlayWelcomeAndStart():
    UI.AppendMessageReply(Config.GetList("欢迎语", []), UI.BeginReplyBlock())

if __name__ == "__main__":
    UI = ChatUI()
    Manager = QuestionManager()
    AI = AIInteraction()
    Config = ConfigManager()

    UI.OnAIRequested = OnAIRequested
    # 延迟 100 毫秒执行初始化
    UI.Root.after(100, PlayWelcomeAndStart)
    UI.Run()