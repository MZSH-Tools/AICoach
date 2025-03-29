import os
import random

# _QuestionItem 类用于封装一道题目的所有信息和功能，
# 包括题干、选项、正确答案、图片路径解析，以及 UI 显示所需的格式化消息结构。
class _QuestionItem:
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
        self.MessageBlocks = self.GenerateMessageBlocks()

    def ResolveImagePath(self, RelativePath, RootPath):
        if not RelativePath:
            return None
        AbsolutePath = os.path.join(RootPath, RelativePath)
        return AbsolutePath if os.path.exists(AbsolutePath) else "[图片未找到]"

    def GenerateMessageBlocks(self) -> list[str]:
        blocks = []
        blocks.append(f"[TEXT] 这是一道{self.Type}题，请选择你认为正确的答案。")
        blocks.append(f"[TEXT] 题目：{self.Stem}")
        if self.Image and self.Image != "[图片未找到]":
            blocks.append(f"[IMAGE] {self.Image}")
        for i, option in enumerate(self.ShuffledOptions):
            label = self.OptionLabels[i]
            blocks.append(f"[TEXT] {label}: {option.get('文本', '')}")
            img_path = option.get("真实图片路径")
            if img_path and img_path != "[图片未找到]":
                blocks.append(f"[IMAGE] {img_path}")
        return blocks
