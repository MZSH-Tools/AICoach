from PySide2 import QtWidgets
from Widget.Item.ListControlWidget import ListControlWidget
from Widget.Item.ImageSelectorWidget import ImageSelectorWidget
from collections import OrderedDict

class OptionWidget(QtWidgets.QWidget):
    def __init__(self, OptionList, OnUpdate, OnImageAdd, Parent=None):
        super().__init__(Parent)
        self.OptionList = OptionList
        self.OnUpdate = OnUpdate
        self.OnImageAdd = OnImageAdd
        self.CurIndex = -1
        OptionWidget.EnsureDataStructure(self.OptionList)
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

        self.ImageWidget = ImageSelectorWidget("图片：")
        self.ImageWidget.SetOnSelect(self.OnSelectImage)
        self.ImageWidget.SetOnDelete(self.OnDeleteImage)
        FormLayout.addRow(self.ImageWidget)

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
    def EnsureDataStructure(OptionList):
        for i, Opt in enumerate(OptionList):
            OptionWidget.EnsureFieldsInOrder(Opt, [
                ("选项ID", lambda i: f"选项{i + 1}"),
                ("文本", ""),
                ("图片", ""),
                ("是否正确", False),
                ("解析", "")
            ], i)

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
        self.ImageWidget.SetText("")
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
            self.ImageWidget.SetText(opt.get("图片", ""))
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
            opt = self.OptionList[self.CurIndex]
            option_id = opt.get("选项ID", "")
            old_file = self.ImageWidget.GetText()
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg)")
            if file_path:
                new_file = self.OnImageAdd(option_id, old_file, file_path)
                self.ImageWidget.SetText(new_file)
                opt["图片"] = new_file
                self.OnUpdate(self.OptionList)

    def OnDeleteImage(self):
        if self.CurIndex != -1 and self.OnImageAdd:
            opt = self.OptionList[self.CurIndex]
            option_id = opt.get("选项ID", "")
            old_file = self.ImageWidget.GetText()
            result = self.OnImageAdd(option_id, old_file, "")
            self.ImageWidget.SetText("")
            opt["图片"] = ""
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
