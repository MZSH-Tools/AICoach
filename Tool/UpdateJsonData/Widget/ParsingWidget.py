from PySide2 import QtWidgets
from Widget.Item.ListControlWidget import ListControlWidget
from collections import OrderedDict

class ParsingWidget(QtWidgets.QWidget):
    def __init__(self, ParsingList, OnUpdate, Parent=None):
        super().__init__(Parent)
        self.ParsingList = ParsingList
        self.OnUpdate = OnUpdate
        self.CurIndex = -1
        ParsingWidget.EnsureDataStructure(self.ParsingList)
        self.OnUpdate(self.ParsingList)
        self.InitUI()

    def InitUI(self):
        Layout = QtWidgets.QHBoxLayout(self)

        self.ListControl = ListControlWidget(
            GetIdList=lambda: [item.get("解析ID", f"解析{i + 1}") for i, item in enumerate(self.ParsingList)],
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

    def OnSelectItem(self, Index):
        if 0 <= Index < len(self.ParsingList):
            self.CurIndex = Index
            Item = self.ParsingList[Index]
            self.EditQuestion.blockSignals(True)
            self.EditQuestion.setText(Item.get("问题", ""))
            self.EditQuestion.blockSignals(False)
            self.EditAnalysis.blockSignals(True)
            self.EditAnalysis.setPlainText(Item.get("解析", ""))
            self.EditAnalysis.blockSignals(False)

    def OnQuestionChanged(self, Text):
        if self.CurIndex != -1:
            self.ParsingList[self.CurIndex]["问题"] = Text
            self.OnUpdate(self.ParsingList)

    def OnAnalysisChanged(self):
        if self.CurIndex != -1:
            self.ParsingList[self.CurIndex]["解析"] = self.EditAnalysis.toPlainText()
            self.OnUpdate(self.ParsingList)

    def HandleAdd(self):
        NewId, Ok = QtWidgets.QInputDialog.getText(self, "添加解析项", "请输入解析ID：")
        if not Ok or not NewId:
            return None
        if self.IsDuplicateId(NewId):
            QtWidgets.QMessageBox.warning(self, "添加失败", f"解析ID “{NewId}” 已存在。")
            return None
        NewItem = {
            "解析ID": NewId,
            "问题": "",
            "解析": ""
        }
        self.ParsingList.append(NewItem)
        self.CurIndex = len(self.ParsingList) - 1
        self.OnUpdate(self.ParsingList)
        return NewId

    def HandleDelete(self, Index):
        if 0 <= Index < len(self.ParsingList):
            self.ParsingList.pop(Index)
            if self.ParsingList:
                self.CurIndex = Index - 1 if Index > 0 else 0
            else:
                self.CurIndex = -1
            self.OnUpdate(self.ParsingList)

    def HandleRename(self, Index, NewId):
        if self.IsDuplicateId(NewId, excludeIndex=Index):
            return False
        self.ParsingList[Index]["解析ID"] = NewId
        self.OnUpdate(self.ParsingList)
        return True

    def HandleReorder(self, IdOrder):
        IdToItem = {p["解析ID"]: p for p in self.ParsingList}
        NewList = [IdToItem[i] for i in IdOrder if i in IdToItem]
        if len(NewList) == len(self.ParsingList):
            self.ParsingList[:] = NewList
            self.OnUpdate(self.ParsingList)

    def IsDuplicateId(self, Id, excludeIndex=None):
        for i, p in enumerate(self.ParsingList):
            if i == excludeIndex:
                continue
            if p.get("解析ID") == Id:
                return True
        return False

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
    def EnsureDataStructure(ParsingList):
        for i, P in enumerate(ParsingList):
            ParsingWidget.EnsureFieldsInOrder(P, [
                ("解析ID", lambda i: f"解析{i + 1}"),
                ("问题", ""),
                ("解析", "")
            ], i)
