from PySide2 import QtWidgets, QtCore
from functools import partial

class ListControlWidget(QtWidgets.QWidget):
    def __init__(self, GetIdList, OnAdd, OnDelete, OnRename, OnReorder, OnSelect, Parent=None):
        super().__init__(Parent)

        self.GetIdList = GetIdList
        self.OnAdd = OnAdd
        self.OnDelete = OnDelete
        self.OnRename = OnRename
        self.OnReorder = OnReorder
        self.OnSelect = OnSelect

        self.CurrentId = None
        self.InitUI()

    def InitUI(self):
        Layout = QtWidgets.QVBoxLayout(self)

        self.ListWidget = QtWidgets.QListWidget()
        self.ListWidget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.ListWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.ListWidget.currentRowChanged.connect(self.OnRowChanged)
        self.ListWidget.model().rowsMoved.connect(self.OnRowsMoved)

        Layout.addWidget(self.ListWidget)

        AddButton = QtWidgets.QPushButton("+")
        AddButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        AddButton.clicked.connect(self.OnAddClicked)
        Layout.addWidget(AddButton)

    def Refresh(self, SelectId=None):
        self.ListWidget.clear()
        IdList = self.GetIdList()

        for Index, ItemId in enumerate(IdList):
            Item = QtWidgets.QListWidgetItem()
            Widget = QtWidgets.QWidget()
            RowLayout = QtWidgets.QHBoxLayout(Widget)
            RowLayout.setContentsMargins(4, 2, 4, 2)

            Label = QtWidgets.QLabel(ItemId)
            RowLayout.addWidget(Label, stretch=1)

            EditButton = QtWidgets.QPushButton("编辑")
            EditButton.clicked.connect(partial(self.OnRenameClicked, Index, Label))
            RowLayout.addWidget(EditButton)

            DeleteButton = QtWidgets.QPushButton("-")
            DeleteButton.clicked.connect(partial(self.OnDeleteClicked, Index))
            RowLayout.addWidget(DeleteButton)

            Item.setSizeHint(Widget.sizeHint())
            self.ListWidget.addItem(Item)
            self.ListWidget.setItemWidget(Item, Widget)

        if IdList:
            # 决定选中哪个 ID
            if SelectId and SelectId in IdList:
                self.CurrentId = SelectId
            elif self.CurrentId not in IdList:
                self.CurrentId = IdList[0]

            # ✅ 延迟选中，确保 UI 稳定后触发 OnSelect
            QtCore.QTimer.singleShot(200, lambda: self.SetCurrentById(self.CurrentId))
        else:
            self.CurrentId = None

    def OnAddClicked(self):
        NewId = self.OnAdd()
        if NewId:
            self.CurrentId = NewId
            self.Refresh(SelectId=NewId)

    def OnDeleteClicked(self, Index):
        IdList = self.GetIdList()
        if 0 <= Index < len(IdList):
            self.OnDelete(Index)
            NewList = self.GetIdList()

            if not NewList:
                self.CurrentId = None
            elif Index - 1 >= 0:
                self.CurrentId = NewList[Index - 1]
            else:
                self.CurrentId = NewList[0]

            self.Refresh(SelectId=self.CurrentId)

    def OnRenameClicked(self, Index, Label):
        OldId = Label.text()
        NewId, Ok = QtWidgets.QInputDialog.getText(self, "编辑ID", "请输入新的ID：", text=OldId)
        if Ok and NewId and NewId != OldId:
            if self.OnRename(Index, NewId):
                self.CurrentId = NewId
                self.Refresh(SelectId=NewId)
            else:
                QtWidgets.QMessageBox.warning(self, "重名错误", f"ID “{NewId}” 已存在，修改失败。")

    def OnRowChanged(self, Index):
        if 0 <= Index < self.ListWidget.count():
            Widget = self.ListWidget.itemWidget(self.ListWidget.item(Index))
            Label = Widget.findChild(QtWidgets.QLabel)
            if Label:
                self.CurrentId = Label.text()
                self.OnSelect(Index)

    def OnRowsMoved(self, *Args):
        NewOrder = []
        for I in range(self.ListWidget.count()):
            Widget = self.ListWidget.itemWidget(self.ListWidget.item(I))
            Label = Widget.findChild(QtWidgets.QLabel)
            if Label:
                NewOrder.append(Label.text())
        self.OnReorder(NewOrder)
        self.Refresh(SelectId=self.CurrentId)

    def SetCurrentById(self, Id):
        for I in range(self.ListWidget.count()):
            Widget = self.ListWidget.itemWidget(self.ListWidget.item(I))
            Label = Widget.findChild(QtWidgets.QLabel)
            if Label and Label.text() == Id:
                self.ListWidget.setCurrentRow(I)
                return

    def SetCurrentIndex(self, Index):
        self.ListWidget.setCurrentRow(Index)
