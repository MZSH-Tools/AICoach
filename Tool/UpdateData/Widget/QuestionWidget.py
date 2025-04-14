from PySide2 import QtWidgets, QtGui, QtCore
import os, shutil
from functools import partial

class QuestionWidget(QtWidgets.QWidget):
    def __init__(self, Questions, OnUpdateCallback=None, Parent=None):
        super().__init__(Parent)
        self.Questions = Questions
        self.OnUpdate = OnUpdateCallback
        self.CurIndex = -1

        self.FileDir = os.path.dirname(os.path.abspath(__file__))
        self.ImageDir = os.path.normpath(os.path.join(self.FileDir, "../../../Assets/Images"))

        self.InitUI()

    def InitUI(self):
        MainLayout = QtWidgets.QHBoxLayout(self)

        # 左侧列表和 + 按钮
        LeftLayout = QtWidgets.QVBoxLayout()
        self.IDList = QtWidgets.QListWidget()
        self.IDList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.IDList.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.IDList.currentRowChanged.connect(self.OnSelectItem)
        self.IDList.model().rowsMoved.connect(self.OnListReordered)
        LeftLayout.addWidget(self.IDList)

        self.AddButton = QtWidgets.QPushButton("+")
        self.AddButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.AddButton.clicked.connect(self.OnAddItem)
        LeftLayout.addWidget(self.AddButton)

        MainLayout.addLayout(LeftLayout, stretch=1)

        # 右侧编辑区
        self.RightWidget = QtWidgets.QWidget()
        RightLayout = QtWidgets.QFormLayout(self.RightWidget)

        self.EditText = QtWidgets.QTextEdit()
        self.EditText.textChanged.connect(self.OnQuestionTextChanged)

        self.ImagePathLabel = QtWidgets.QLabel("(题干图片路径)")
        self.SelectImageButton = QtWidgets.QPushButton("选择题干图片")
        self.SelectImageButton.clicked.connect(self.OnSelectImage)

        RightLayout.addRow("题目文本：", self.EditText)
        RightLayout.addRow("图片路径：", self.ImagePathLabel)
        RightLayout.addRow("", self.SelectImageButton)

        MainLayout.addWidget(self.RightWidget, stretch=3)

        self.RefreshList()

    def RefreshList(self):
        self.IDList.clear()
        for i, Q in enumerate(self.Questions):
            item = QtWidgets.QListWidgetItem()
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(widget)
            layout.setContentsMargins(4, 2, 4, 2)

            label = QtWidgets.QLabel(Q.get("题目ID", "未知ID"))
            layout.addWidget(label, stretch=1)

            editButton = QtWidgets.QPushButton("编辑")
            editButton.clicked.connect(partial(self.OnEditItem, i))
            layout.addWidget(editButton)

            deleteButton = QtWidgets.QPushButton("-")
            deleteButton.clicked.connect(partial(self.OnDeleteItem, i))
            layout.addWidget(deleteButton)

            item.setSizeHint(widget.sizeHint())
            self.IDList.addItem(item)
            self.IDList.setItemWidget(item, widget)

    def OnSelectItem(self, Index):
        if 0 <= Index < len(self.Questions):
            self.CurIndex = Index
            Q = self.Questions[Index]
            self.EditText.blockSignals(True)
            self.EditText.setPlainText(Q.get("题目", {}).get("文本", ""))
            self.EditText.blockSignals(False)
            self.ImagePathLabel.setText(Q.get("题目", {}).get("图片", ""))

    def IsDuplicateID(self, ID, excludeIndex=None):
        return any(q["题目ID"] == ID for i, q in enumerate(self.Questions) if i != excludeIndex)

    def ShowDuplicateWarning(self, ID):
        QtWidgets.QMessageBox.warning(self, "ID重复", f"题目ID '{ID}' 已存在，请使用唯一的ID。")

    def OnAddItem(self):
        NewID, ok = QtWidgets.QInputDialog.getText(self, "新增题目", "请输入新题目的ID:")
        if not ok or not NewID:
            return

        if self.IsDuplicateID(NewID):
            self.ShowDuplicateWarning(NewID)
            return

        NewQ = {
            "题目ID": NewID,
            "题目": {"文本": "", "图片": ""},
            "题目类型": "单选",
            "选项": [],
            "解析库": []
        }
        self.Questions.append(NewQ)
        self.RefreshList()
        self.IDList.setCurrentRow(len(self.Questions) - 1)
        self.EmitUpdate()

    def OnDeleteItem(self, Index):
        if 0 <= Index < len(self.Questions):
            self.Questions.pop(Index)
            self.RefreshList()

            if len(self.Questions) == 0:
                self.CurIndex = -1
                self.ClearRightPanel()
                return self.EmitUpdate()

            # 设置为前一个索引，如果不存在则为 0
            self.CurIndex = Index - 1 if Index - 1 >= 0 else 0
            self.IDList.setCurrentRow(self.CurIndex)
            self.OnSelectItem(self.CurIndex)

            self.EmitUpdate()

    def OnEditItem(self, Index):
        if 0 <= Index < len(self.Questions):
            currentID = self.Questions[Index]["题目ID"]
            NewID, ok = QtWidgets.QInputDialog.getText(self, "编辑题目ID", "请输入新的题目ID:", text=currentID)
            if ok and NewID:
                if self.IsDuplicateID(NewID, excludeIndex=Index):
                    self.ShowDuplicateWarning(NewID)
                    return
                self.Questions[Index]["题目ID"] = NewID
                self.RefreshList()
                self.IDList.setCurrentRow(Index)
                self.EmitUpdate()

    def OnQuestionTextChanged(self):
        if self.CurIndex != -1 and self.CurIndex < len(self.Questions):
            NewText = self.EditText.toPlainText()
            self.Questions[self.CurIndex]["题目"]["文本"] = NewText
            self.EmitUpdate()

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
                self.EmitUpdate()

    def OnListReordered(self, *args):
        newQuestions = []
        for i in range(self.IDList.count()):
            itemWidget = self.IDList.itemWidget(self.IDList.item(i))
            label = itemWidget.findChild(QtWidgets.QLabel)
            if label:
                idText = label.text()
                for q in self.Questions:
                    if q["题目ID"] == idText:
                        newQuestions.append(q)
                        break
        self.Questions = newQuestions
        self.EmitUpdate()

    def ClearRightPanel(self):
        self.EditText.blockSignals(True)
        self.EditText.clear()
        self.EditText.blockSignals(False)
        self.ImagePathLabel.setText("")

    def EmitUpdate(self):
        if self.OnUpdate:
            self.OnUpdate(self.Questions)
