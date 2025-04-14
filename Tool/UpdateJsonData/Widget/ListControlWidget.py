from PySide2 import QtWidgets, QtCore

class ListControlWidget(QtWidgets.QWidget):
    def __init__(self, GetIdList, OnAdd, OnDelete, OnRename, OnReorder, OnSelect):
        super().__init__()
        self.GetIdList = GetIdList
        self.OnAdd = OnAdd
        self.OnDelete = OnDelete
        self.OnRename = OnRename
        self.OnReorder = OnReorder
        self.OnSelect = OnSelect
        self.CurrentId = None
        self.CurIndex = -1
        self.InitUI()

    def InitUI(self):
        Layout = QtWidgets.QVBoxLayout(self)
        self.ListWidget = QtWidgets.QListWidget()
        self.ListWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ListWidget.customContextMenuRequested.connect(self.OnContextMenu)
        self.ListWidget.setDragEnabled(True)
        self.ListWidget.setAcceptDrops(True)
        self.ListWidget.setDropIndicatorShown(True)
        self.ListWidget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.ListWidget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.ListWidget.currentRowChanged.connect(self.OnSelect)
        Layout.addWidget(self.ListWidget)

        self.AddButton = QtWidgets.QPushButton("+ 添加")
        self.AddButton.clicked.connect(self.HandleAdd)
        Layout.addWidget(self.AddButton)

    def Refresh(self):
        self.ListWidget.clear()
        for Id in self.GetIdList():
            self.ListWidget.addItem(Id)

        if self.ListWidget.count() > 0 and self.CurrentId is None:
            QtCore.QTimer.singleShot(200, lambda: self.SetCurrentIndex(0))

    def SetCurrentIndex(self, Index):
        if 0 <= Index < self.ListWidget.count():
            self.ListWidget.setCurrentRow(Index)
            self.CurIndex = Index
            self.CurrentId = self.GetIdList()[Index]
            self.OnSelect(Index)

    def HandleAdd(self):
        NewId = self.OnAdd()
        if NewId:
            self.Refresh()
            for Index, Id in enumerate(self.GetIdList()):
                if Id == NewId:
                    self.SetCurrentIndex(Index)
                    break

    def OnContextMenu(self, Pos):
        Item = self.ListWidget.itemAt(Pos)
        if not Item:
            return
        Index = self.ListWidget.row(Item)
        Menu = QtWidgets.QMenu()
        RenameAction = Menu.addAction("✏️ 重命名")
        DeleteAction = Menu.addAction("🗑️ 删除")
        Action = Menu.exec_(self.ListWidget.mapToGlobal(Pos))

        if Action == RenameAction:
            CurId = self.GetIdList()[Index]
            NewId, Ok = QtWidgets.QInputDialog.getText(self, "重命名", "请输入新ID：", text=CurId)
            if Ok and NewId and NewId != CurId:
                if self.OnRename(Index, NewId):
                    self.Refresh()
                    self.SetCurrentIndex(Index)
        elif Action == DeleteAction:
            self.OnDelete(Index)
            self.Refresh()

    def HandleReorder(self, IdOrder):
        self.OnReorder(IdOrder)
        self.Refresh()
