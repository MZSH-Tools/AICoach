import json
import random
import os
from Config.ConfigManager import ConfigManager

class QuestionManager:
    def __init__(self):
        self.Config = ConfigManager()
        RootPath = os.path.dirname(os.path.dirname(__file__))
        RelativePath = self.Config.GetString("题库路径", "Data/QuestionBank.json")
        self.QuestionPath = os.path.join(RootPath, RelativePath)
        self.AllQuestions = []
        self.DoneQuestionIDs = set()
        self.OptionLabels = self.Config.ConfigData.get("选项编号", ["A", "B", "C", "D", "E", "F"])
        self.LoadQuestions()

    def LoadQuestions(self):
        if not os.path.exists(self.QuestionPath):
            print(f"[警告] 题库文件不存在：{self.QuestionPath}")
            return

        with open(self.QuestionPath, "r", encoding="utf-8-sig") as File:
            try:
                Data = json.load(File)
                self.AllQuestions = Data.get("题库", [])
            except Exception as Error:
                print(f"[错误] 加载题库失败：{str(Error)}")

    def GetRandomQuestion(self):
        AllowRepeat = self.Config.GetBool("允许重复抽题", False)

        if AllowRepeat:
            QuestionPool = self.AllQuestions
        else:
            QuestionPool = [Question for Question in self.AllQuestions if Question.get("题目ID") not in self.DoneQuestionIDs]

        if not QuestionPool:
            print("[提示] 所有题目已完成，无题可抽。")
            return None

        QuestionData = random.choice(QuestionPool)
        self.DoneQuestionIDs.add(QuestionData.get("题目ID"))

        Options = QuestionData.get("选项", [])[:]
        if self.Config.GetBool("打乱选项", True):
            random.shuffle(Options)

        Question = {
            "题目ID": QuestionData.get("题目ID"),
            "题干": QuestionData.get("题目", {}).get("文本", ""),
            "图片": QuestionData.get("题目", {}).get("图片"),
            "题目类型": QuestionData.get("题目类型"),
            "选项": Options,
            "原始选项": QuestionData.get("选项", []),
            "正确答案": [Option["文本"] for Option in QuestionData.get("选项", []) if Option.get("是否正确")],
            "解析库": QuestionData.get("解析库", [])
        }

        Question["展示文本"] = self.FormatForDisplay(Question)

        return Question

    def FormatForDisplay(self, Question):
        Type = Question.get("题目类型", "单选")
        Intro = "这是一道判断题，请回答你觉得正确与否。"
        if "判断" not in Type:
            Intro = "这是一道单选题，请回答你觉得正确的答案。"

        Text = f"{Intro}\n题目：{Question.get('题干', '')}"

        if Question.get("图片"):
            Text += f"\n图片：{Question.get('图片')}"

        Text += "\n选项："
        for Index, Option in enumerate(Question.get("选项", [])):
            Label = self.OptionLabels[Index] if Index < len(self.OptionLabels) else f"选项{Index+1}"
            Text += f"\n{Label}: {Option.get('文本', '')}"
            if Option.get("图片"):
                Text += f"\n图片：{Option.get('图片')}"

        return Text

    def MarkQuestionAsDone(self, QuestionID):
        self.DoneQuestionIDs.add(QuestionID)


if __name__ == "__main__":
    Manager = QuestionManager()
    Sample = Manager.GetRandomQuestion()
    if Sample:
        print("✅ 抽取到一题：")
        print(Sample["展示文本"])
        print("正确答案:", Sample["正确答案"])
    else:
        print("❌ 没有题目可用")
