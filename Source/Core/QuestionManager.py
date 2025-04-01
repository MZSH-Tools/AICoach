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
        self.OptionLabels = self.Config.ConfigData.get("选项编号", ["A", "B", "C", "D", "E", "F"])
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

        self.CurrentQuestion = _QuestionItem(QuestionData, self.ProjectRoot, self.OptionLabels)
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

    def GetCorrectAnswers(self):
        if self.CurrentQuestion:
            return self.CurrentQuestion.CorrectAnswers
        else:
            return []

if __name__ == "__main__":
    Manager = QuestionManager()
    if Manager.NextRandomQuestion():
        print("✅ 抽取到一题：")
        for Block in Manager.GetMessageBlocks():
            print(Block)
        print("正确答案:", Manager.GetCorrectAnswers())
    else:
        print("❌ 没有题目可用")