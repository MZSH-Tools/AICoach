import os
import random

# _QuestionItem 类用于封装一道题目的所有信息和功能，
# 包括题干、选项、正确答案、图片路径解析，以及 UI 显示所需的格式化消息结构。
class _QuestionItem:
    def __init__(self, RawData: dict, RootPath: str, RandomOption: bool, OptionLabels: list[str]):
        self.ID = RawData.get("题目ID")
        self.Type = RawData.get("题目类型", "单选")
        self.Stem = RawData.get("题目", {}).get("文本", "")
        self.Image = self.ResolveImagePath(RawData.get("题目", {}).get("图片"), RootPath)
        self.Options = RawData.get("选项", [])
        self.OptionLabels = OptionLabels[:len(self.Options)]
        if RandomOption:
            random.shuffle(self.Options)
        for Option in self.Options:
            Option["真实图片路径"] = self.ResolveImagePath(Option.get("图片"), RootPath)
        self.CorrectAnswers = [OptionLabels[i] for i, Option in enumerate(self.Options)  if Option.get("是否正确")]
        self.Explanation = RawData.get("解析库", [])
        self.MessageBlocks = self.GenerateMessageBlocks()
        self.RawData = RawData

    @staticmethod
    def ResolveImagePath(RelativePath, RootPath):
        if not RelativePath:
            return None
        ImageRoot = os.path.join(RootPath, "Assets/Images")
        AbsolutePath = os.path.join(ImageRoot, RelativePath)
        return AbsolutePath if os.path.exists(AbsolutePath) else "[图片未找到]"

    def GenerateMessageBlocks(self) -> list[str]:
        Blocks = [
            f"[TEXT] 这是一道{self.Type}题，请选择你认为正确的答案。",
            f"[TEXT] 题目：{self.Stem}"
        ]
        if self.Image and self.Image != "[图片未找到]":
            Blocks.append(f"[IMAGE] {self.Image}")
        for i, Option in enumerate(self.Options):
            Label = self.OptionLabels[i]
            Blocks.append(f"[TEXT] {Label}: {Option.get('文本', '')}")
            ImagePath = Option.get("真实图片路径")
            if ImagePath and ImagePath != "[图片未找到]":
                Blocks.append(f"[IMAGE] {ImagePath}")
        return Blocks
