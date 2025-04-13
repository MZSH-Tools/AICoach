from PySide2 import QtWidgets
import os, shutil

class QuestionWidget(QtWidgets.QWidget):
    def __init__(self, Questions, OnUpdateCallback=None, Parent=None):
        """
        参数:
            Questions: 题库列表（List[Dict]），格式必须为 JSON 中的“题库”部分。
            OnUpdateCallback: 回调函数，接收修改后的 Questions 用于保存。
        """
        super().__init__(Parent)
        self.Questions = Questions
        self.OnUpdate = OnUpdateCallback
        self.CurIndex = -1

        self.FileDir = os.path.dirname(os.path.abspath(__file__))
        self.ImageDir = os.path.normpath(os.path.join(self.FileDir, "../../../Assets/Images"))

        self.InitUI()

    def InitUI(self):
        MainLayout = QtWidgets.QHBoxLayout(self)

        # 左侧题目ID列表 + 按钮
        LeftLayout = QtWidgets.QVBoxLayout()
        self.IDList = QtWidgets.QListWidget()
        for Q in self.Questions:
            self.IDList.addItem(Q.get("题目ID", "未知ID"))
        self.IDList.currentRowChanged.connect(self.OnSelectItem)

        AddButton = QtWidgets.QPushButton("新增题目")
        AddButton.clicked.connect(self.OnAddItem)
        DelButton = QtWidgets.QPushButton("删除题目")
        DelButton.clicked.connect(self.OnDeleteItem)

        LeftLayout.addWidget(self.IDList)
        LeftLayout.addWidget(AddButton)
        LeftLayout.addWidget(DelButton)

        # 右侧题目编辑区域
        self.RightWidget = QtWidgets.QWidget()
        RightLayout = QtWidgets.QFormLayout(self.RightWidget)

        self.EditQuestionID = QtWidgets.QLineEdit()
        self.EditQuestionID.textChanged.connect(self.OnQuestionIDChanged)

        self.EditText = QtWidgets.QTextEdit()
        self.EditText.textChanged.connect(self.OnQuestionTextChanged)

        self.ImagePathLabel = QtWidgets.QLabel("(题干图片路径)")
        self.SelectImageButton = QtWidgets.QPushButton("选择题干图片")
        self.SelectImageButton.clicked.connect(self.OnSelectImage)

        RightLayout.addRow("题目ID：", self.EditQuestionID)
        RightLayout.addRow("题目文本：", self.EditText)
        RightLayout.addRow("图片路径：", self.ImagePathLabel)
        RightLayout.addRow("", self.SelectImageButton)

        MainLayout.addLayout(LeftLayout, stretch=1)
        MainLayout.addWidget(self.RightWidget, stretch=3)

    def OnSelectItem(self, Index):
        if 0 <= Index < len(self.Questions):
            self.CurIndex = Index
            Q = self.Questions[Index]
            self.EditQuestionID.setText(Q.get("题目ID", ""))
            self.EditText.setPlainText(Q.get("题目", {}).get("文本", ""))
            self.ImagePathLabel.setText(Q.get("题目", {}).get("图片", ""))

    def OnAddItem(self):
        NewQ = {
            "题目ID": f"S99.99.{len(self.Questions)+1:03d}",
            "题目": {"文本": "", "图片": ""},
            "题目类型": "单选",
            "选项": [],
            "解析库": []
        }
        self.Questions.append(NewQ)
        self.IDList.addItem(NewQ["题目ID"])
        self.IDList.setCurrentRow(len(self.Questions) - 1)
        self.EmitUpdate()

    def OnDeleteItem(self):
        Row = self.IDList.currentRow()
        if 0 <= Row < len(self.Questions):
            self.Questions.pop(Row)
            self.IDList.takeItem(Row)
            self.ClearRightPanel()
            self.EmitUpdate()

    def ClearRightPanel(self):
        self.EditQuestionID.clear()
        self.EditText.clear()
        self.ImagePathLabel.setText("")

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
            if self.CurIndex != -1:
                self.Questions[self.CurIndex]["题目"]["图片"] = RelPath
                self.EmitUpdate()

    def OnQuestionIDChanged(self, NewText):
        if self.CurIndex != -1:
            self.Questions[self.CurIndex]["题目ID"] = NewText
            self.IDList.item(self.CurIndex).setText(NewText)
            self.EmitUpdate()

    def OnQuestionTextChanged(self):
        if self.CurIndex != -1:
            NewText = self.EditText.toPlainText()
            self.Questions[self.CurIndex]["题目"]["文本"] = NewText
            self.EmitUpdate()

    def EmitUpdate(self):
        if self.OnUpdate:
            self.OnUpdate(self.Questions)
