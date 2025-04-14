from PySide2 import QtWidgets, QtGui, QtCore
import os, shutil
from functools import partial
from Widget.ListControlWidget import ListControlWidget

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

        # 左侧列表组件
        self.ListControl = ListControlWidget(
            get_id_list=lambda: [q["题目ID"] for q in self.Questions],
            on_add=self.HandleAddQuestion,
            on_delete=self.HandleDeleteQuestion,
            on_rename=self.HandleRenameQuestion,
            on_reorder=self.HandleReorderQuestions,
            on_select=self.OnSelectItem
        )
        MainLayout.addWidget(self.ListControl, stretch=1)

        # 右侧编辑区
        self.RightWidget = QtWidgets.QScrollArea()
        self.RightWidget.setWidgetResizable(True)
        RightContainer = QtWidgets.QWidget()
        self.RightLayout = QtWidgets.QVBoxLayout(RightContainer)

        # 题目文本
        self.EditText = QtWidgets.QTextEdit()
        self.EditText.textChanged.connect(self.OnQuestionTextChanged)
        self.RightLayout.addWidget(QtWidgets.QLabel("题目文本："))
        self.RightLayout.addWidget(self.EditText)

        # 题干图片
        self.ImagePathLabel = QtWidgets.QLabel("(题干图片路径)")
        self.SelectImageButton = QtWidgets.QPushButton("选择题干图片")
        self.SelectImageButton.clicked.connect(self.OnSelectImage)
        self.RightLayout.addWidget(self.ImagePathLabel)
        self.RightLayout.addWidget(self.SelectImageButton)

        # 选项区域（占位）
        self.RightLayout.addWidget(QtWidgets.QLabel("选项："))
        self.OptionList = QtWidgets.QListWidget()
        self.AddOptionButton = QtWidgets.QPushButton("添加选项")
        self.RightLayout.addWidget(self.OptionList)
        self.RightLayout.addWidget(self.AddOptionButton)

        # 解析库区域（占位）
        self.RightLayout.addWidget(QtWidgets.QLabel("解析库："))
        self.ParsingList = QtWidgets.QListWidget()
        self.AddParsingButton = QtWidgets.QPushButton("添加解析项")
        self.RightLayout.addWidget(self.ParsingList)
        self.RightLayout.addWidget(self.AddParsingButton)

        # 题目解析
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

    def HandleAddQuestion(self):
        new_id, ok = QtWidgets.QInputDialog.getText(self, "添加题目", "请输入题目ID：")
        if not ok or not new_id:
            return None
        if self.IsDuplicateID(new_id):
            QtWidgets.QMessageBox.warning(self, "添加失败", f"ID “{new_id}” 已存在。")
            return None
        new_question = {
            "题目ID": new_id,
            "题目": {"文本": "", "图片": ""},
            "题目类型": "单选",
            "选项": [],
            "解析库": [],
            "题目解析": ""
        }
        self.Questions.append(new_question)
        self.CurIndex = len(self.Questions) - 1
        self.OnUpdate(self.Questions)
        return new_id

    def HandleDeleteQuestion(self, index):
        if 0 <= index < len(self.Questions):
            self.Questions.pop(index)
            if self.Questions:
                self.CurIndex = index - 1 if index - 1 >= 0 else 0
                self.OnSelectItem(self.CurIndex)
            else:
                self.CurIndex = -1
                self.ClearRightPanel()
            self.OnUpdate(self.Questions)

    def HandleRenameQuestion(self, index, new_id):
        if self.IsDuplicateID(new_id, exclude_index=index):
            return False
        self.Questions[index]["题目ID"] = new_id
        self.OnUpdate(self.Questions)
        return True

    def HandleReorderQuestions(self, new_id_list):
        new_order = []
        id_to_question = {q["题目ID"]: q for q in self.Questions}
        for qid in new_id_list:
            if qid in id_to_question:
                new_order.append(id_to_question[qid])
        self.Questions = new_order
        self.OnUpdate(self.Questions)

    def IsDuplicateID(self, new_id, exclude_index=None):
        for i, q in enumerate(self.Questions):
            if i == exclude_index:
                continue
            if q["题目ID"] == new_id:
                return True
        return False

    def OnQuestionTextChanged(self):
        if self.CurIndex != -1 and self.CurIndex < len(self.Questions):
            NewText = self.EditText.toPlainText()
            self.Questions[self.CurIndex]["题目"]["文本"] = NewText
            self.OnUpdate(self.Questions)

    def OnAnalysisTextChanged(self):
        if self.CurIndex != -1 and self.CurIndex < len(self.Questions):
            NewText = self.AnalysisText.toPlainText()
            self.Questions[self.CurIndex].setdefault("题目解析", "")
            self.Questions[self.CurIndex]["题目解析"] = NewText
            self.OnUpdate(self.Questions)

    def OnSelectImage(self):
        FilePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择题干图片", self.ImageDir, "Images (*.png *.jpg *.jpeg)")
        if FilePath:
            ImageName = os.path.basename(FilePath)
            TargetPath = os.path.join(self.ImageDir, ImageName)
            if not os.path.exists(TargetPath):
                try:
                    shutil.copy(FilePath, TargetPath)
                except Exception as e:
                    print(f"复制图片失败：{e}")
            RelPath = os.path.relpath(TargetPath, self.FileDir).replace("\\", "/")
            self.ImagePathLabel.setText(RelPath)
            if self.CurIndex != -1 and self.CurIndex < len(self.Questions):
                self.Questions[self.CurIndex]["题目"]["图片"] = RelPath
                self.OnUpdate(self.Questions)

    def EnsureDataStructure(self, Questions):
        for q in Questions:
            q.setdefault("题目", {}).setdefault("文本", "")
            q["题目"].setdefault("图片", "")
            q.setdefault("题目类型", "单选")
            q.setdefault("选项", [])
            q.setdefault("解析库", [])
            q.setdefault("题目解析", "")


        self.EditText.blockSignals(True)
        self.EditText.clear()
        self.EditText.blockSignals(False)
        self.ImagePathLabel.setText("")
        self.AnalysisText.blockSignals(True)
        self.AnalysisText.clear()
        self.AnalysisText.blockSignals(False)
