from PySide2 import QtWidgets,QtCore
from Widget.ListControlWidget import ListControlWidget
import os

class OptionWidget(QtWidgets.QWidget):
    def __init__(self, OptionList, OnUpdate, OnImageAdd, OnImageDelete, Parent=None):
        super().__init__(Parent)
        self.OptionList = OptionList
        self.OnUpdate = OnUpdate
        self.OnImageAdd = OnImageAdd
        self.OnImageDelete = OnImageDelete
        self.CurIndex = -1
        self.InitUI()

    def InitUI(self):
        Layout = QtWidgets.QHBoxLayout(self)
        self.ListControl = ListControlWidget(
            GetIdList=lambda: [opt.get("选项ID", f"选项{idx+1}") for idx, opt in enumerate(self.OptionList)],
            OnAdd=self.HandleAdd,
            OnDelete=self.HandleDelete,
            OnRename=self.HandleRename,
            OnReorder=self.HandleReorder,
            OnSelect=self.OnSelectItem
        )
        Layout.addWidget(self.ListControl, stretch=1)

        Form = QtWidgets.QFormLayout()
        self.EditText = QtWidgets.QTextEdit()
        self.EditText.textChanged.connect(self.OnTextChanged)
        Form.addRow("文本：", self.EditText)

        self.ImagePathLabel = QtWidgets.QLabel("(图片路径)")
        self.SelectImageButton = QtWidgets.QPushButton("选择图片")
        self.SelectImageButton.clicked.connect(self.OnSelectImage)
        Form.addRow("图片：", self.ImagePathLabel)
        Form.addRow("", self.SelectImageButton)

        self.CorrectCheck = QtWidgets.QCheckBox("是否正确")
        self.CorrectCheck.stateChanged.connect(self.OnCorrectChanged)
        Form.addRow("", self.CorrectCheck)

        self.ParseText = QtWidgets.QTextEdit()
        self.ParseText.textChanged.connect(self.OnParseChanged)
        Form.addRow("解析：", self.ParseText)

        RightWidget = QtWidgets.QWidget()
        RightWidget.setLayout(Form)
        Layout.addWidget(RightWidget, stretch=3)
        self.RefreshList()

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

    def OnSelectItem(self, Index):
        if 0 <= Index < len(self.OptionList):
            self.CurIndex = Index
            Opt = self.OptionList[Index]
            self.EditText.blockSignals(True)
            self.EditText.setPlainText(Opt.get("文本", ""))
            self.EditText.blockSignals(False)
            self.ImagePathLabel.setText(Opt.get("图片", ""))
            self.CorrectCheck.setChecked(Opt.get("是否正确", False))
            self.ParseText.blockSignals(True)
            self.ParseText.setPlainText(Opt.get("解析", ""))
            self.ParseText.blockSignals(False)

    def OnTextChanged(self):
        if self.CurIndex != -1:
            self.OptionList[self.CurIndex]["文本"] = self.EditText.toPlainText()
            self.OnUpdate(self.OptionList)

    def OnParseChanged(self):
        if self.CurIndex != -1:
            self.OptionList[self.CurIndex]["解析"] = self.ParseText.toPlainText()
            self.OnUpdate(self.OptionList)

    def OnCorrectChanged(self, State):
        if self.CurIndex != -1:
            self.OptionList[self.CurIndex]["是否正确"] = (State == QtCore.Qt.Checked)
            self.OnUpdate(self.OptionList)

    def OnSelectImage(self):
        Path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg)")
        if Path and self.OnImageAdd and self.CurIndex != -1:
            RelPath = self.OnImageAdd(Path)
            self.ImagePathLabel.setText(RelPath)
            self.OptionList[self.CurIndex]["图片"] = RelPath
            self.OnUpdate(self.OptionList)

    def HandleAdd(self):
        NewId, Ok = QtWidgets.QInputDialog.getText(self, "添加选项", "请输入选项ID：")
        if not Ok or not NewId:
            return None
        if self.IsDuplicateId(NewId):
            QtWidgets.QMessageBox.warning(self, "添加失败", f"选项ID “{NewId}” 已存在。")
            return None
        NewOpt = {
            "选项ID": NewId,
            "文本": "",
            "图片": "",
            "是否正确": False,
            "解析": ""
        }
        self.OptionList.append(NewOpt)
        self.CurIndex = len(self.OptionList) - 1
        self.OnUpdate(self.OptionList)
        return NewId

    def HandleDelete(self, Index):
        if 0 <= Index < len(self.OptionList):
            self.OptionList.pop(Index)
            if self.OptionList:
                self.CurIndex = Index - 1 if Index - 1 >= 0 else 0
            else:
                self.CurIndex = -1
            self.OnUpdate(self.OptionList)

    def HandleRename(self, Index, NewId):
        if self.IsDuplicateId(NewId, excludeIndex=Index):
            return False
        self.OptionList[Index]["选项ID"] = NewId
        self.OnUpdate(self.OptionList)
        return True

    def HandleReorder(self, IdOrder):
        IdToOpt = {opt.get("选项ID"): opt for opt in self.OptionList}
        NewList = [IdToOpt[oid] for oid in IdOrder if oid in IdToOpt]
        if len(NewList) == len(self.OptionList):
            self.OptionList[:] = NewList
            self.OnUpdate(self.OptionList)

    def IsDuplicateId(self, Id, excludeIndex=None):
        for I, Opt in enumerate(self.OptionList):
            if I == excludeIndex:
                continue
            if Opt.get("选项ID") == Id:
                return True
        return False

    def ClearEditor(self):
        self.EditText.blockSignals(True)
        self.EditText.clear()
        self.EditText.blockSignals(False)
        self.ImagePathLabel.setText("")
        self.CorrectCheck.setChecked(False)
        self.ParseText.blockSignals(True)
        self.ParseText.clear()
        self.ParseText.blockSignals(False)
