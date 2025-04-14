from PySide2 import QtWidgets, QtCore, QtGui
from functools import partial

class ListControlWidget(QtWidgets.QWidget):
    def __init__(self, get_id_list, on_add, on_delete, on_rename, on_reorder, on_select, parent=None):
        super().__init__(parent)
        self.get_id_list = get_id_list
        self.on_add = on_add
        self.on_delete = on_delete
        self.on_rename = on_rename
        self.on_reorder = on_reorder
        self.on_select = on_select

        self.InitUI()

    def InitUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.ListWidget = QtWidgets.QListWidget()
        self.ListWidget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.ListWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.ListWidget.currentRowChanged.connect(self.on_select)
        self.ListWidget.model().rowsMoved.connect(self.on_rows_moved)
        layout.addWidget(self.ListWidget)

        AddButton = QtWidgets.QPushButton("+")
        AddButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        AddButton.clicked.connect(self.on_add_clicked)
        layout.addWidget(AddButton)

    def Refresh(self):
        self.ListWidget.clear()
        for i, item_id in enumerate(self.get_id_list()):
            item = QtWidgets.QListWidgetItem()
            widget = QtWidgets.QWidget()
            row_layout = QtWidgets.QHBoxLayout(widget)
            row_layout.setContentsMargins(4, 2, 4, 2)

            label = QtWidgets.QLabel(item_id)
            row_layout.addWidget(label, stretch=1)

            edit_btn = QtWidgets.QPushButton("编辑")
            edit_btn.clicked.connect(partial(self.on_rename_clicked, i, label))
            row_layout.addWidget(edit_btn)

            del_btn = QtWidgets.QPushButton("-")
            del_btn.clicked.connect(partial(self.on_delete_clicked, i))
            row_layout.addWidget(del_btn)

            item.setSizeHint(widget.sizeHint())
            self.ListWidget.addItem(item)
            self.ListWidget.setItemWidget(item, widget)

    def on_add_clicked(self):
        new_id = self.on_add()
        if new_id:
            self.Refresh()

    def on_delete_clicked(self, index):
        self.on_delete(index)
        self.Refresh()

    def on_rename_clicked(self, index, label):
        old_id = label.text()
        new_id, ok = QtWidgets.QInputDialog.getText(self, "编辑ID", "请输入新的ID：", text=old_id)
        if ok and new_id and new_id != old_id:
            if self.on_rename(index, new_id):
                self.Refresh()
            else:
                QtWidgets.QMessageBox.warning(self, "重名错误", f"ID “{new_id}” 已存在，修改失败。")

    def on_rows_moved(self, *args):
        new_order = []
        for i in range(self.ListWidget.count()):
            item_widget = self.ListWidget.itemWidget(self.ListWidget.item(i))
            label = item_widget.findChild(QtWidgets.QLabel)
            if label:
                new_order.append(label.text())
        self.on_reorder(new_order)
        self.Refresh()

    def set_current_index(self, index):
        self.ListWidget.setCurrentRow(index)
