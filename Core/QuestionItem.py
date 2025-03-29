import random
import os

# 面向一“题”，代表一条题目的全部数据和与之相关的逻辑。
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
