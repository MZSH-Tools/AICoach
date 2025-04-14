from PySide2 import QtWidgets
from Widget.ListControlWidget import ListControlWidget

class OptionWidget(QtWidgets.QWidget):
    def __init__(self, OptionList, OnUpdate, OnImageAdd, OnImageDelete, Parent=None):
        super().__init__(Parent)
        self.OptionList = OptionList
        self.OnUpdate = OnUpdate
        self.OnImageAdd = OnImageAdd
        self.OnImageDelete = OnImageDelete
        self.CurIndex = -1
        self.EnsureDataStructure(self.OptionList)
        self.OnUpdate(self.OptionList)
        self.InitUI()

    def InitUI(self):
        Layout = QtWidgets.QHBoxLayout(self)

        self.ListControl = ListControlWidget(
            GetIdList=lambda: [opt.get("选项ID", f"选项{i+1}") for i, opt in enumerate(self.OptionList)],
            OnAdd=self.HandleAdd,
            OnDelete=self.HandleDelete,
            OnRename=self.HandleRename,
            OnReorder=self.HandleReorder,
            OnSelect=self.OnSelectItem
        )
        Layout.addWidget(self.ListControl, stretch=1)

        FormLayout = QtWidgets.QFormLayout()

        self.EditText = QtWidgets.QLineEdit()
        self.EditText.textChanged.connect(self.OnTextChanged)
        FormLayout.addRow("文本：", self.EditText)

        self.ImagePathLabel = QtWidgets.QLabel("(选项图片路径)")
        self.SelectImageButton = QtWidgets.QPushButton("选择图片")
        self.SelectImageButton.clicked.connect(self.OnSelectImage)
        FormLayout.addRow(self.ImagePathLabel, self.SelectImageButton)

        self.IsCorrectCheck = QtWidgets.QCheckBox("是否为正确答案")
        self.IsCorrectCheck.stateChanged.connect(self.OnCorrectChanged)
        FormLayout.addRow(self.IsCorrectCheck)

        self.EditAnalysis = QtWidgets.QTextEdit()
        self.EditAnalysis.textChanged.connect(self.OnAnalysisChanged)
        FormLayout.addRow("解析：", self.EditAnalysis)

        RightWidget = QtWidgets.QWidget()
        RightWidget.setLayout(FormLayout)
        Layout.addWidget(RightWidget, stretch=3)

        self.RefreshList()

    def EnsureDataStructure(self, OptionList):
        for i, opt in enumerate(OptionList):
            opt.setdefault("选项ID", f"选项{i+1}")
            opt.setdefault("文本", "")
            opt.setdefault("图片", "")
            opt.setdefault("是否正确", False)
            opt.setdefault("解析", "")

    def RefreshList(self):
        self.ListControl.Refresh()
        if self.OptionList:
            if self.CurIndex == -1 or self.CurIndex >= len(self.OptionList):
                self.CurIndex = 0
            self.ListControl.SetCurrentIndex(self.CurIndex)
            self.OnSelectItem(self.CurIndex)
        else:
            self.CurIndex = -1
            self.ClearEditor()

    def ClearEditor(self):
        self.EditText.blockSignals(True)
        self.EditText.clear()
        self.EditText.blockSignals(False)
        self.ImagePathLabel.setText("")
        self.IsCorrectCheck.blockSignals(True)
        self.IsCorrectCheck.setChecked(False)
        self.IsCorrectCheck.blockSignals(False)
        self.EditAnalysis.blockSignals(True)
        self.EditAnalysis.clear()
        self.EditAnalysis.blockSignals(False)

    def OnSelectItem(self, index):
        if 0 <= index < len(self.OptionList):
            self.CurIndex = index
            opt = self.OptionList[index]
            self.EditText.blockSignals(True)
            self.EditText.setText(opt.get("文本", ""))
            self.EditText.blockSignals(False)
            self.ImagePathLabel.setText(opt.get("图片", ""))
            self.IsCorrectCheck.blockSignals(True)
            self.IsCorrectCheck.setChecked(opt.get("是否正确", False))
            self.IsCorrectCheck.blockSignals(False)
            self.EditAnalysis.blockSignals(True)
            self.EditAnalysis.setPlainText(opt.get("解析", ""))
            self.EditAnalysis.blockSignals(False)

    def OnTextChanged(self, text):
        if self.CurIndex != -1:
            self.OptionList[self.CurIndex]["文本"] = text
            self.OnUpdate(self.OptionList)

    def OnAnalysisChanged(self):
        if self.CurIndex != -1:
            self.OptionList[self.CurIndex]["解析"] = self.EditAnalysis.toPlainText()
            self.OnUpdate(self.OptionList)

    def OnCorrectChanged(self, state):
        if self.CurIndex != -1:
            self.OptionList[self.CurIndex]["是否正确"] = (state == QtWidgets.Qt.Checked)
            self.OnUpdate(self.OptionList)

    def OnSelectImage(self):
        if self.OnImageAdd and self.CurIndex != -1:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg)")
            if file_path:
                opt = self.OptionList[self.CurIndex]
                rel_path = self.OnImageAdd(file_path, opt.get("题目ID", ""), opt.get("选项ID", ""))
                self.ImagePathLabel.setText(rel_path)
                opt["图片"] = rel_path
                self.OnUpdate(self.OptionList)

    def HandleAdd(self):
        new_id, ok = QtWidgets.QInputDialog.getText(self, "添加选项", "请输入选项ID：")
        if not ok or not new_id:
            return None
        if self.IsDuplicateId(new_id):
            QtWidgets.QMessageBox.warning(self, "添加失败", f"选项ID “{new_id}” 已存在。")
            return None
        new_opt = {"选项ID": new_id, "文本": "", "图片": "", "是否正确": False, "解析": ""}
        self.OptionList.append(new_opt)
        self.CurIndex = len(self.OptionList) - 1
        self.OnUpdate(self.OptionList)
        return new_id

    def HandleDelete(self, index):
        if 0 <= index < len(self.OptionList):
            self.OptionList.pop(index)
            if self.OptionList:
                self.CurIndex = index - 1 if index > 0 else 0
            else:
                self.CurIndex = -1
            self.OnUpdate(self.OptionList)

    def HandleRename(self, index, new_id):
        if self.IsDuplicateId(new_id, excludeIndex=index):
            return False
        self.OptionList[index]["选项ID"] = new_id
        self.OnUpdate(self.OptionList)
        return True

    def HandleReorder(self, id_order):
        id_to_opt = {opt["选项ID"]: opt for opt in self.OptionList}
        self.OptionList[:] = [id_to_opt[i] for i in id_order if i in id_to_opt]
        self.OnUpdate(self.OptionList)

    def IsDuplicateId(self, id, excludeIndex=None):
        for i, opt in enumerate(self.OptionList):
            if i == excludeIndex:
                continue
            if opt.get("选项ID") == id:
                return True
        return False
