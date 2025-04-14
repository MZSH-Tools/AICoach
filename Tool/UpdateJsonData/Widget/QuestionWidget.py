from PySide2 import QtWidgets
from Widget.ListControlWidget import ListControlWidget
from Widget.OptionWidget import OptionWidget
from Widget.ParsingWidget import ParsingWidget
import os

class QuestionWidget(QtWidgets.QWidget):
    def __init__(self, Questions, OnUpdateCallback=None, OnImageAdd=None, OnImageDelete=None, Parent=None):
        super().__init__(Parent)
        self.Questions = Questions
        self.OnUpdate = OnUpdateCallback
        self.OnImageAdd = OnImageAdd
        self.OnImageDelete = OnImageDelete
        self.CurIndex = -1
        self.FileDir = os.path.dirname(os.path.abspath(__file__))
        self.InitUI()
        self.EnsureDataStructure(self.Questions)

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

        self.ImagePathLabel = QtWidgets.QLabel("(题干图片路径)")
        self.SelectImageButton = QtWidgets.QPushButton("选择题干图片")
        self.SelectImageButton.clicked.connect(self.OnSelectImage)
        RightLayout.addWidget(self.ImagePathLabel)
        RightLayout.addWidget(self.SelectImageButton)

        self.OptionWidget = OptionWidget([], self.OnOptionUpdated, self.OnImageAdd, self.OnImageDelete)
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
            self.ImagePathLabel.setText(Q["题目"].get("图片", ""))
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
            RelPath = self.OnImageAdd(Path)
            self.ImagePathLabel.setText(RelPath)
            self.Questions[self.CurIndex]["题目"]["图片"] = RelPath
            self.OnUpdate(self.Questions)

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
        self.ImagePathLabel.setText("")
        self.AnalysisText.blockSignals(True)
        self.AnalysisText.clear()
        self.AnalysisText.blockSignals(False)

    def EnsureDataStructure(self, Questions):
        for Q in Questions:
            Q.setdefault("题目", {}).setdefault("文本", "")
            Q["题目"].setdefault("图片", "")
            Q.setdefault("题目类型", "单选")
            Q.setdefault("选项", [])
            Q.setdefault("解析库", [])
            Q.setdefault("题目解析", "")
            for I, Opt in enumerate(Q["选项"]):
                Opt.setdefault("选项ID", f"选项{I + 1}")
                Opt.setdefault("文本", "")
                Opt.setdefault("图片", "")
                Opt.setdefault("是否正确", False)
                Opt.setdefault("解析", "")
            for I, Parse in enumerate(Q["解析库"]):
                Parse.setdefault("解析ID", f"解析{I + 1}")
                Parse.setdefault("问题", "")
                Parse.setdefault("解析", "")

        # ✅ 清空 UI 初始状态
        self.EditText.blockSignals(True)
        self.EditText.clear()
        self.EditText.blockSignals(False)
        self.ImagePathLabel.setText("")
        self.AnalysisText.blockSignals(True)
        self.AnalysisText.clear()
        self.AnalysisText.blockSignals(False)
