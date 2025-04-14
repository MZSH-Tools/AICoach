from PySide2 import QtWidgets, QtGui, QtCore
import os, shutil
from functools import partial
from Widget.ListControlWidget import ListControlWidget
from Widget.OptionWidget import OptionWidget
from Widget.ParsingWidget import ParsingWidget

class QuestionWidget(QtWidgets.QWidget):
    def __init__(self, Questions, OnUpdateCallback=None, Parent=None):
        super().__init__(Parent)
        self.Questions = Questions
        self.OnUpdate = OnUpdateCallback
        self.CurIndex = -1

        self.FileDir = os.path.dirname(os.path.abspath(__file__))
        self.ImageDir = os.path.normpath(os.path.join(self.FileDir, "../../../Assets/Images"))

        self.InitUI()
        self.EnsureDataStructure(self.Questions)

    def InitUI(self):
        MainLayout = QtWidgets.QHBoxLayout(self)

        self.ListControl = ListControlWidget(
            GetIdList=lambda: [q["题目ID"] for q in self.Questions],
            OnAdd=self.HandleAddQuestion,
            OnDelete=self.HandleDeleteQuestion,
            OnRename=self.HandleRenameQuestion,
            OnReorder=self.HandleReorderQuestions,
            OnSelect=self.OnSelectItem
        )
        MainLayout.addWidget(self.ListControl, stretch=1)

        self.RightWidget = QtWidgets.QScrollArea()
        self.RightWidget.setWidgetResizable(True)
        RightContainer = QtWidgets.QWidget()
        self.RightLayout = QtWidgets.QVBoxLayout(RightContainer)

        self.EditText = QtWidgets.QTextEdit()
        self.EditText.textChanged.connect(self.OnQuestionTextChanged)
        self.RightLayout.addWidget(QtWidgets.QLabel("题目文本："))
        self.RightLayout.addWidget(self.EditText)

        self.ImagePathLabel = QtWidgets.QLabel("(题干图片路径)")
        self.SelectImageButton = QtWidgets.QPushButton("选择题干图片")
        self.SelectImageButton.clicked.connect(self.OnSelectImage)
        self.RightLayout.addWidget(self.ImagePathLabel)
        self.RightLayout.addWidget(self.SelectImageButton)

        self.RightLayout.addWidget(QtWidgets.QLabel("选项："))
        self.OptionWidget = OptionWidget([], self.OnOptionUpdated, self.ImageDir)
        self.RightLayout.addWidget(self.OptionWidget)

        self.RightLayout.addWidget(QtWidgets.QLabel("解析库："))
        self.ParsingWidget = ParsingWidget([], self.OnParsingUpdated)
        self.RightLayout.addWidget(self.ParsingWidget)

        self.RightLayout.addWidget(QtWidgets.QLabel("题目解析："))
        self.AnalysisText = QtWidgets.QTextEdit()
        self.AnalysisText.textChanged.connect(self.OnAnalysisTextChanged)
        self.RightLayout.addWidget(self.AnalysisText)

        self.RightWidget.setWidget(RightContainer)
        MainLayout.addWidget(self.RightWidget, stretch=3)

        self.RefreshList()

    def RefreshList(self):
        self.ListControl.Refresh()

    def OnSelectItem(self, Index):
        if 0 <= Index < len(self.Questions):
            self.CurIndex = Index
            Q = self.Questions[Index]

            self.EditText.blockSignals(True)
            self.EditText.setPlainText(Q.get("题目", {}).get("文本", ""))
            self.EditText.blockSignals(False)

            self.ImagePathLabel.setText(Q.get("题目", {}).get("图片", ""))

            self.AnalysisText.blockSignals(True)
            self.AnalysisText.setPlainText(Q.get("题目解析") or "")
            self.AnalysisText.blockSignals(False)

            if hasattr(self, "OptionWidget"):
                self.OptionWidget.OptionList = Q["选项"]
                self.OptionWidget.CurIndex = -1
                self.OptionWidget.RefreshList()

            if hasattr(self, "ParsingWidget"):
                self.ParsingWidget.ParsingList = Q["解析库"]
                self.ParsingWidget.CurIndex = -1
                self.ParsingWidget.RefreshList()

    def OnOptionUpdated(self, UpdatedList):
        if self.CurIndex != -1:
            self.Questions[self.CurIndex]["选项"] = UpdatedList
            self.OnUpdate(self.Questions)

    def OnParsingUpdated(self, UpdatedList):
        if self.CurIndex != -1:
            self.Questions[self.CurIndex]["解析库"] = UpdatedList
            self.OnUpdate(self.Questions)

    def HandleAddQuestion(self):
        NewId, Ok = QtWidgets.QInputDialog.getText(self, "添加题目", "请输入题目ID：")
        if not Ok or not NewId:
            return None
        if self.IsDuplicateID(NewId):
            QtWidgets.QMessageBox.warning(self, "添加失败", f"ID “{NewId}” 已存在。")
            return None
        NewQuestion = {
            "题目ID": NewId,
            "题目": {"文本": "", "图片": ""},
            "题目类型": "单选",
            "选项": [],
            "解析库": [],
            "题目解析": ""
        }
        self.Questions.append(NewQuestion)
        self.CurIndex = len(self.Questions) - 1
        self.OnUpdate(self.Questions)
        return NewId

    def HandleDeleteQuestion(self, Index):
        if 0 <= Index < len(self.Questions):
            self.Questions.pop(Index)
            if self.Questions:
                self.CurIndex = Index - 1 if Index - 1 >= 0 else 0
                self.OnSelectItem(self.CurIndex)
            else:
                self.CurIndex = -1
                self.ClearRightPanel()
            self.OnUpdate(self.Questions)

    def HandleRenameQuestion(self, Index, NewId):
        if self.IsDuplicateID(NewId, exclude_index=Index):
            return False
        self.Questions[Index]["题目ID"] = NewId
        self.OnUpdate(self.Questions)
        return True

    def HandleReorderQuestions(self, IdOrder):
        IdToQ = {q["题目ID"]: q for q in self.Questions}
        NewOrder = [IdToQ[qid] for qid in IdOrder if qid in IdToQ]
        self.Questions = NewOrder
        self.OnUpdate(self.Questions)

    def IsDuplicateID(self, NewId, exclude_index=None):
        for I, Q in enumerate(self.Questions):
            if I == exclude_index:
                continue
            if Q["题目ID"] == NewId:
                return True
        return False

    def OnQuestionTextChanged(self):
        if self.CurIndex != -1:
            self.Questions[self.CurIndex]["题目"]["文本"] = self.EditText.toPlainText()
            self.OnUpdate(self.Questions)

    def OnAnalysisTextChanged(self):
        if self.CurIndex != -1:
            self.Questions[self.CurIndex].setdefault("题目解析", "")
            self.Questions[self.CurIndex]["题目解析"] = self.AnalysisText.toPlainText()
            self.OnUpdate(self.Questions)

    def OnSelectImage(self):
        Path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择题干图片", self.ImageDir, "Images (*.png *.jpg *.jpeg)")
        if Path:
            FileName = os.path.basename(Path)
            Target = os.path.join(self.ImageDir, FileName)
            if not os.path.exists(Target):
                try:
                    shutil.copy(Path, Target)
                except Exception as e:
                    print(f"复制图片失败：{e}")
            Rel = os.path.relpath(Target, self.FileDir).replace("\\", "/")
            self.ImagePathLabel.setText(Rel)
            if self.CurIndex != -1:
                self.Questions[self.CurIndex]["题目"]["图片"] = Rel
                self.OnUpdate(self.Questions)

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

        # 清空 UI
        self.EditText.blockSignals(True)
        self.EditText.clear()
        self.EditText.blockSignals(False)
        self.ImagePathLabel.setText("")
        self.AnalysisText.blockSignals(True)
        self.AnalysisText.clear()
        self.AnalysisText.blockSignals(False)

