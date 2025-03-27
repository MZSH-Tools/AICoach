import json
import random
import os
from Config.ConfigManager import ConfigManager

class QuestionItem:
    def __init__(self, RawData: dict, RootPath: str, OptionLabels: list[str]):
        self.ID = RawData.get("题目ID")
        self.Type = RawData.get("题目类型", "单选")
        self.Stem = RawData.get("题目", {}).get("文本", "")
        self.Image = self.ResolveImagePath(RawData.get("题目", {}).get("图片"), RootPath)
        self.OriginalOptions = RawData.get("选项", [])
        self.OptionLabels = OptionLabels
        self.ShuffledOptions = self.OriginalOptions[:]
        random.shuffle(self.ShuffledOptions)
        for Option in self.ShuffledOptions:
            Option["真实图片路径"] = self.ResolveImagePath(Option.get("图片"), RootPath)
        self.CorrectAnswers = [Option["文本"] for Option in self.OriginalOptions if Option.get("是否正确")]
        self.Explanation = RawData.get("解析库", [])

    def ResolveImagePath(self, RelativePath, RootPath):
        if not RelativePath:
            return None
        AbsolutePath = os.path.join(RootPath, RelativePath)
        return AbsolutePath if os.path.exists(AbsolutePath) else "[图片未找到]"

    def GetFormattedText(self):
        Intro = f"这是一道{self.Type}题，请回答你觉得正确的选项。"
        Text = f"{Intro}\n题目：{self.Stem}"
        if self.Image and self.Image != "[图片未找到]":
            Text += f"\n[显示图片]"
        Text += "\n选项："
        for Index, Option in enumerate(self.ShuffledOptions):
            Label = self.OptionLabels[Index] if Index < len(self.OptionLabels) else f"选项{Index+1}"
            Text += f"\n{Label}: {Option.get('文本', '')}"
            ImgPath = Option.get("真实图片路径")
            if ImgPath and ImgPath != "[图片未找到]":
                Text += f"\n[显示图片]"
        return Text

class QuestionManager:
    _Instance = None

    def __new__(cls):
        if cls._Instance is None:
            cls._Instance = super(QuestionManager, cls).__new__(cls)
            cls._Instance._Initialized = False
        return cls._Instance

    def __init__(self):
        if self._Initialized:
            return
        self._Initialized = True

        self.Config = ConfigManager()
        RootPath = os.path.dirname(os.path.dirname(__file__))
        RelativePath = self.Config.GetString("题库路径", "Data/QuestionBank.json")
        self.QuestionPath = os.path.join(RootPath, RelativePath)
        self.ProjectRoot = RootPath
        self.AllQuestions = []
        self.DoneQuestionIDs = set()
        self.OptionLabels = self.Config.ConfigData.get("选项编号", ["A", "B", "C", "D", "E", "F"])
        self.CurrentQuestion = None
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
        self.CurrentQuestion = QuestionItem(QuestionData, self.ProjectRoot, self.OptionLabels)
        return self.CurrentQuestion

    def GetCurQuestion(self):
        return self.CurrentQuestion

    def MarkQuestionAsDone(self, QuestionID):
        self.DoneQuestionIDs.add(QuestionID)


if __name__ == "__main__":
    Manager = QuestionManager()
    Sample = Manager.GetRandomQuestion()
    if Sample:
        print("✅ 抽取到一题：")
        print(Sample.GetFormattedText())
        print("正确答案:", Sample.CorrectAnswers)
    else:
        print("❌ 没有题目可用")