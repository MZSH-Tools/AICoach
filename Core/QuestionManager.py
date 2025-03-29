from Core.QuestionItem import _QuestionItem

import json
import random
import os
from Config.ConfigManager import ConfigManager

# 面向“题库”，是题目池子的管理者，负责加载、抽题、配置、切换题目。
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
        self.QuestionPool = []
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
                self.QuestionPool = self.AllQuestions[:]
            except Exception as Error:
                print(f"[错误] 加载题库失败：{str(Error)}")

    def GetRandomQuestion(self):
        ReloadIfEmpty = self.Config.GetBool("题库为空时重新加载", True)
        ShuffleEachTime = self.Config.GetBool("每次抽题打乱顺序", True)
        RemoveQuestion = self.Config.GetBool("在题库中移除已抽题目", True)

        if ReloadIfEmpty and not self.QuestionPool:
            self.ResetPool()

        if ShuffleEachTime:
            self.ShufflePool()

        if self.QuestionPool:
            if RemoveQuestion:
                QuestionData = self.QuestionPool.pop(0)
            else:
                QuestionData = self.QuestionPool[0]
            self.CurrentQuestion = _QuestionItem(QuestionData, self.ProjectRoot, self.OptionLabels)
        else:
            print("[提示] 所有题目已完成，无题可抽。")
            self.CurrentQuestion = None

        return self.CurrentQuestion

    def ShufflePool(self):
        if self.QuestionPool:
            random.shuffle(self.QuestionPool)

    def ResetPool(self):
        self.QuestionPool = self.AllQuestions[:]

    def GetCurQuestion(self):
        return self.CurrentQuestion

if __name__ == "__main__":
    Manager = QuestionManager()
    Sample = Manager.GetRandomQuestion()
    if Sample:
        print("✅ 抽取到一题：")
        print(Sample.GetFormattedText())
        print("正确答案:", Sample.CorrectAnswers)
    else:
        print("❌ 没有题目可用")
