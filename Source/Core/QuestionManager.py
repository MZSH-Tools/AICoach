from Source.Core.QuestionItem import _QuestionItem

import json
import random
import os
from Source.Config.ConfigManager import ConfigManager

# QuestionManager 类负责加载题库、抽取题目、管理当前题目，并统一提供外部访问接口，是题库模块的核心调度器。
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
        self.ProjectRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        RelativePath = self.Config.GetString("题库路径", "Data/QuestionBank.json")
        self.QuestionPath = os.path.join(self.ProjectRoot, RelativePath)
        self.AllQuestions = []
        self.QuestionPool = []
        self.CurrentQuestion = None
        self.Explanation = []
        self.LoadQuestions()

    def LoadQuestions(self):
        if not os.path.exists(self.QuestionPath):
            print(f"[警告] 题库文件不存在：{self.QuestionPath}")
            return

        with open(self.QuestionPath, "r", encoding="utf-8-sig") as File:
            try:
                Data = json.load(File)
                self.AllQuestions = Data.get("题库", [])
                self.QuestionPool = self.AllQuestions[:]
                self.Explanation = Data.get("公共解析库", [])
            except Exception as Error:
                print(f"[错误] 加载题库失败：{str(Error)}")

    def ShufflePool(self):
        if self.QuestionPool:
            random.shuffle(self.QuestionPool)

    def ResetPool(self):
        self.QuestionPool = self.AllQuestions[:]

    # 切换下一个随机题目
    def NextRandomQuestion(self)->bool():
        ReloadIfEmpty = self.Config.GetBool("题库为空时重新加载", True)
        ShuffleEachTime = self.Config.GetBool("每次抽题打乱顺序", True)
        RemoveQuestion = self.Config.GetBool("在题库中移除已抽题目", True)

        if ReloadIfEmpty and not self.QuestionPool:
            self.ResetPool()

        if ShuffleEachTime:
            self.ShufflePool()

        if not self.QuestionPool:
            print("[提示] 所有题目已完成，无题可抽。")
            self.CurrentQuestion = None
            return False

        if RemoveQuestion:
            QuestionData = self.QuestionPool.pop(0)
        else:
            QuestionData = self.QuestionPool[0]

        self.CurrentQuestion = _QuestionItem(
            QuestionData,
            self.ProjectRoot,
            self.Config.GetBool("打乱选项", True),
            self.Config.ConfigData.get("选项编号", ["A", "B", "C", "D", "E", "F"]))
        return True

    def GetMessageBlocks(self) -> list[str]:
        if self.CurrentQuestion:
            return self.CurrentQuestion.MessageBlocks
        else:
            return []

    def GetExplanation(self):
        if self.CurrentQuestion:
            return self.CurrentQuestion.Explanation + self.Explanation
        else:
            return self.Explanation

    def CheckAnswer(self, Answer):
        if self.CurrentQuestion is None:
            return False,[]
        StrList = []
        MaxChar = 1
        if self.CurrentQuestion.Type == "多选":
            MaxChar = len(self.CurrentQuestion.Options)

        if len(Answer) > MaxChar:
            StrList.append(f"[TEXT]字符数过多超过题目限制，最多支持{MaxChar}个字符，请重新填写")
            return False, StrList

        for Char in Answer:
            StrList.append("")
            if Char not in  self.CurrentQuestion.OptionLabels:
                StrList[-1] += f"[TEXT]字符'{Char}'不属于选项{self.CurrentQuestion.OptionLabels}, 请重新输入"
                return False, StrList
            StrList[-1] += f"[TEXT]选项{Char}:"
            CharIndex = self.CurrentQuestion.OptionLabels.index(Char)
            Explanation = self.CurrentQuestion.Options[CharIndex].get("解析", "")
            if Char in self.CurrentQuestion.CorrectAnswers:
                StrList[-1] += "正确！"
                if self.Config.GetBool("正确解析", False):
                    StrList.append(f"[TEXT]解析:{Explanation}")
            else:
                StrList[-1] += "错误！"
                if self.Config.GetBool("错误解析", True):
                    StrList.append(f"[TEXT]解析:{Explanation}")
        return True, StrList

if __name__ == "__main__":
    Manager = QuestionManager()
    if Manager.NextRandomQuestion():
        print("✅ 抽取到一题：")
        for Block in Manager.GetMessageBlocks():
            print(Block)
        print("正确答案:", Manager.CurrentQuestion.CorrectAnswers)
        for Str in Manager.CheckAnswer("1"):
            print(Str)
    else:
        print("❌ 没有题目可用")