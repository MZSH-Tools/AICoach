from PySide2 import QtWidgets
from Widget.Item.ListControlWidget import ListControlWidget
from Widget.Item.ImageSelectorWidget import ImageSelectorWidget
from Widget.OptionWidget import OptionWidget
from Widget.ParsingWidget import ParsingWidget
from collections import OrderedDict
import os

class QuestionWidget(QtWidgets.QWidget):
    def __init__(self, Questions, OnUpdateCallback=None, OnImageAdd=None, Parent=None):
        super().__init__(Parent)
        self.Questions = Questions
        self.OnUpdate = OnUpdateCallback
        self.OnImageAdd = OnImageAdd
        self.CurIndex = -1
        self.FileDir = os.path.dirname(os.path.abspath(__file__))
        QuestionWidget.EnsureDataStructure(self.Questions)
        self.OnUpdate(self.Questions)
        self.InitUI()

    def InitUI(self):
        Layout = QtWidgets.QHBoxLayout(self)
        self.ListControl = ListControlWidget(
            GetIdList=lambda: [q["题目ID"] for q in self.Questions],
            OnAdd=self.HandleAddQuestion,
            OnDelete=self.HandleDeleteQuestion,
            OnRename=self.HandleRenameQuestion,
            OnReorder=self.HandleReorderQuestions,
            OnSelect=self.OnSelectItem
        )
        Layout.addWidget(self.ListControl, stretch=1)

        RightLayout = QtWidgets.QVBoxLayout()

        self.EditText = QtWidgets.QTextEdit()
        self.EditText.textChanged.connect(self.OnQuestionTextChanged)
        RightLayout.addWidget(QtWidgets.QLabel("题目文本："))
        RightLayout.addWidget(self.EditText)

        self.ImageWidget = ImageSelectorWidget("图片：")
        self.ImageWidget.SetOnSelect(self.OnSelectImage)
        self.ImageWidget.SetOnDelete(self.OnDeleteImage)
        RightLayout.addWidget(self.ImageWidget)

        self.OptionWidget = OptionWidget([], self.OnOptionUpdated, self.HandleOptionImageChange)
        RightLayout.addWidget(QtWidgets.QLabel("选项："))
        RightLayout.addWidget(self.OptionWidget)

        self.ParsingWidget = ParsingWidget([], self.OnParsingUpdated)
        RightLayout.addWidget(QtWidgets.QLabel("解析库："))
        RightLayout.addWidget(self.ParsingWidget)

        self.AnalysisText = QtWidgets.QTextEdit()
        self.AnalysisText.textChanged.connect(self.OnAnalysisTextChanged)
        RightLayout.addWidget(QtWidgets.QLabel("题目解析："))
        RightLayout.addWidget(self.AnalysisText)

        RightWidget = QtWidgets.QWidget()
        RightWidget.setLayout(RightLayout)
        Layout.addWidget(RightWidget, stretch=3)

        self.RefreshList()

    def RefreshList(self):
        self.ListControl.Refresh()
        if self.Questions:
            if self.CurIndex == -1 or self.CurIndex >= len(self.Questions):
                self.CurIndex = 0
            self.ListControl.SetCurrentIndex(self.CurIndex)
            self.OnSelectItem(self.CurIndex)
        else:
            self.CurIndex = -1
            self.ClearEditor()

    def OnSelectItem(self, Index):
        if 0 <= Index < len(self.Questions):
            self.CurIndex = Index
            Q = self.Questions[Index]
            self.EditText.blockSignals(True)
            self.EditText.setPlainText(Q["题目"].get("文本", ""))
            self.EditText.blockSignals(False)
            self.ImageWidget.SetText(Q["题目"].get("图片", ""))
            self.AnalysisText.blockSignals(True)
            self.AnalysisText.setPlainText(Q.get("题目解析", ""))
            self.AnalysisText.blockSignals(False)
            self.OptionWidget.OptionList = Q["选项"]
            self.OptionWidget.RefreshList()
            self.ParsingWidget.ParsingList = Q["解析库"]
            self.ParsingWidget.RefreshList()

    def OnOptionUpdated(self, UpdatedList):
        if self.CurIndex != -1:
            self.Questions[self.CurIndex]["选项"] = UpdatedList
            self.OnUpdate(self.Questions)

    def OnParsingUpdated(self, UpdatedList):
        if self.CurIndex != -1:
            self.Questions[self.CurIndex]["解析库"] = UpdatedList
            self.OnUpdate(self.Questions)

    def OnQuestionTextChanged(self):
        if self.CurIndex != -1:
            self.Questions[self.CurIndex]["题目"]["文本"] = self.EditText.toPlainText()
            self.OnUpdate(self.Questions)

    def OnAnalysisTextChanged(self):
        if self.CurIndex != -1:
            self.Questions[self.CurIndex]["题目解析"] = self.AnalysisText.toPlainText()
            self.OnUpdate(self.Questions)

    def OnSelectImage(self):
        Path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg)")
        if Path and self.OnImageAdd and self.CurIndex != -1:
            OldFileName = self.ImageWidget.GetText()
            Qid = self.Questions[self.CurIndex]["题目ID"]
            NewFileName = self.OnImageAdd(Qid, OldFileName, Path)
            self.ImageWidget.SetText(NewFileName)
            self.Questions[self.CurIndex]["题目"]["图片"] = NewFileName
            self.OnUpdate(self.Questions)

    def OnDeleteImage(self):
        if self.CurIndex != -1 and self.OnImageAdd:
            OldFileName = self.ImageWidget.GetText()
            Qid = self.Questions[self.CurIndex]["题目ID"]
            Result = self.OnImageAdd(Qid, OldFileName, "")
            self.ImageWidget.SetText("")
            self.Questions[self.CurIndex]["题目"]["图片"] = ""
            self.OnUpdate(self.Questions)

    def HandleOptionImageChange(self, OptionId, OldFileName, SourcePath):
        if self.CurIndex != -1 and self.OnImageAdd:
            Qid = self.Questions[self.CurIndex]["题目ID"]
            SetName = f"{Qid}_{OptionId}"
            return self.OnImageAdd(SetName, OldFileName, SourcePath)
        return ""

    def HandleAddQuestion(self):
        NewId, Ok = QtWidgets.QInputDialog.getText(self, "添加题目", "请输入题目ID：")
        if not Ok or not NewId:
            return None
        if self.IsDuplicateId(NewId):
            QtWidgets.QMessageBox.warning(self, "添加失败", f"题目ID “{NewId}” 已存在。")
            return None
        NewItem = {
            "题目ID": NewId,
            "题目": {"文本": "", "图片": ""},
            "题目类型": "单选",
            "选项": [],
            "解析库": [],
            "题目解析": ""
        }
        self.Questions.append(NewItem)
        self.CurIndex = len(self.Questions) - 1
        self.OnUpdate(self.Questions)
        return NewId

    def HandleDeleteQuestion(self, Index):
        if 0 <= Index < len(self.Questions):
            self.Questions.pop(Index)
            if self.Questions:
                self.CurIndex = Index - 1 if Index - 1 >= 0 else 0
            else:
                self.CurIndex = -1
            self.OnUpdate(self.Questions)

    def HandleRenameQuestion(self, Index, NewId):
        if self.IsDuplicateId(NewId, excludeIndex=Index):
            return False
        self.Questions[Index]["题目ID"] = NewId
        self.OnUpdate(self.Questions)
        return True

    def HandleReorderQuestions(self, IdOrder):
        IdToItem = {q["题目ID"]: q for q in self.Questions}
        NewList = [IdToItem[qid] for qid in IdOrder if qid in IdToItem]
        if len(NewList) == len(self.Questions):
            self.Questions[:] = NewList
            self.OnUpdate(self.Questions)

    def IsDuplicateId(self, Id, excludeIndex=None):
        for I, Item in enumerate(self.Questions):
            if I == excludeIndex:
                continue
            if Item.get("题目ID") == Id:
                return True
        return False

    def ClearEditor(self):
        self.EditText.blockSignals(True)
        self.EditText.clear()
        self.EditText.blockSignals(False)
        self.ImageWidget.SetText("")
        self.AnalysisText.blockSignals(True)
        self.AnalysisText.clear()
        self.AnalysisText.blockSignals(False)

    @staticmethod
    def EnsureFieldsInOrder(DictObj, TemplateList, Index=0):
        Ordered = OrderedDict()
        for Key, Default in TemplateList:
            if callable(Default):
                Ordered[Key] = DictObj.get(Key, Default(Index))
            else:
                Ordered[Key] = DictObj.get(Key, Default)
        DictObj.clear()
        DictObj.update(Ordered)

    @staticmethod
    def EnsureDataStructure(Questions):
        for i, Q in enumerate(Questions):
            QuestionWidget.EnsureFieldsInOrder(Q, [
                ("题目ID", ""),
                ("题目", {"文本": "", "图片": ""}),
                ("题目类型", "单选"),
                ("选项", []),
                ("解析库", []),
                ("题目解析", "")
            ], i)
            OptionWidget.EnsureDataStructure(Q["选项"])
            ParsingWidget.EnsureDataStructure(Q["解析库"])
