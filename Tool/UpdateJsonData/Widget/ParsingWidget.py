from PySide2 import QtWidgets
from Widget.ListControlWidget import ListControlWidget

class ParsingWidget(QtWidgets.QWidget):
    def __init__(self, ParsingList, OnUpdate, Parent=None):
        super().__init__(Parent)
        self.ParsingList = ParsingList
        self.OnUpdate = OnUpdate
        self.CurIndex = -1
        self.EnsureDataStructure(self.ParsingList)
        self.OnUpdate(self.ParsingList)
        self.InitUI()

    def InitUI(self):
        Layout = QtWidgets.QHBoxLayout(self)

        self.ListControl = ListControlWidget(
            GetIdList=lambda: [item.get("解析ID", f"解析{idx+1}") for idx, item in enumerate(self.ParsingList)],
            OnAdd=self.HandleAdd,
            OnDelete=self.HandleDelete,
            OnRename=self.HandleRename,
            OnReorder=self.HandleReorder,
            OnSelect=self.OnSelectItem
        )
        Layout.addWidget(self.ListControl, stretch=1)

        FormLayout = QtWidgets.QFormLayout()

        self.EditQuestion = QtWidgets.QLineEdit()
        self.EditQuestion.textChanged.connect(self.OnQuestionChanged)
        FormLayout.addRow("问题：", self.EditQuestion)

        self.EditAnalysis = QtWidgets.QTextEdit()
        self.EditAnalysis.textChanged.connect(self.OnAnalysisChanged)
        FormLayout.addRow("解析：", self.EditAnalysis)

        RightWidget = QtWidgets.QWidget()
        RightWidget.setLayout(FormLayout)
        Layout.addWidget(RightWidget, stretch=3)

        self.RefreshList()

    def EnsureDataStructure(self, ParsingList):
        for i, p in enumerate(ParsingList):
            p.setdefault("解析ID", f"解析{i+1}")
            p.setdefault("问题", "")
            p.setdefault("解析", "")

    def RefreshList(self):
        self.ListControl.Refresh()
        if self.ParsingList:
            if self.CurIndex == -1 or self.CurIndex >= len(self.ParsingList):
                self.CurIndex = 0
            self.ListControl.SetCurrentIndex(self.CurIndex)
            self.OnSelectItem(self.CurIndex)
        else:
            self.CurIndex = -1
            self.ClearEditor()

    def ClearEditor(self):
        self.EditQuestion.blockSignals(True)
        self.EditQuestion.clear()
        self.EditQuestion.blockSignals(False)
        self.EditAnalysis.blockSignals(True)
        self.EditAnalysis.clear()
        self.EditAnalysis.blockSignals(False)

    def OnSelectItem(self, index):
        if 0 <= index < len(self.ParsingList):
            self.CurIndex = index
            item = self.ParsingList[index]
            self.EditQuestion.blockSignals(True)
            self.EditQuestion.setText(item.get("问题", ""))
            self.EditQuestion.blockSignals(False)
            self.EditAnalysis.blockSignals(True)
            self.EditAnalysis.setPlainText(item.get("解析", ""))
            self.EditAnalysis.blockSignals(False)

    def OnQuestionChanged(self, text):
        if self.CurIndex != -1:
            self.ParsingList[self.CurIndex]["问题"] = text
            self.OnUpdate(self.ParsingList)

    def OnAnalysisChanged(self):
        if self.CurIndex != -1:
            self.ParsingList[self.CurIndex]["解析"] = self.EditAnalysis.toPlainText()
            self.OnUpdate(self.ParsingList)

    def HandleAdd(self):
        new_id, ok = QtWidgets.QInputDialog.getText(self, "添加解析项", "请输入解析ID：")
        if not ok or not new_id:
            return None
        if self.IsDuplicateId(new_id):
            QtWidgets.QMessageBox.warning(self, "添加失败", f"解析ID “{new_id}” 已存在。")
            return None
        new_item = {"解析ID": new_id, "问题": "", "解析": ""}
        self.ParsingList.append(new_item)
        self.CurIndex = len(self.ParsingList) - 1
        self.OnUpdate(self.ParsingList)
        return new_id

    def HandleDelete(self, index):
        if 0 <= index < len(self.ParsingList):
            self.ParsingList.pop(index)
            if self.ParsingList:
                self.CurIndex = index - 1 if index > 0 else 0
            else:
                self.CurIndex = -1
            self.OnUpdate(self.ParsingList)

    def HandleRename(self, index, new_id):
        if self.IsDuplicateId(new_id, excludeIndex=index):
            return False
        self.ParsingList[index]["解析ID"] = new_id
        self.OnUpdate(self.ParsingList)
        return True

    def HandleReorder(self, id_order):
        id_to_item = {p["解析ID"]: p for p in self.ParsingList}
        new_list = [id_to_item[i] for i in id_order if i in id_to_item]
        if len(new_list) == len(self.ParsingList):
            self.ParsingList[:] = new_list
            self.OnUpdate(self.ParsingList)

    def IsDuplicateId(self, id, excludeIndex=None):
        for i, p in enumerate(self.ParsingList):
            if i == excludeIndex:
                continue
            if p.get("解析ID") == id:
                return True
        return False
