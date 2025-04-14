from PySide2 import QtWidgets

class ImageSelectorWidget(QtWidgets.QWidget):
    def __init__(self, LabelText="图片：", OnSelect=None, OnDelete=None, Parent=None):
        super().__init__(Parent)
        self.OnSelectCallback = OnSelect
        self.OnDeleteCallback = OnDelete

        Layout = QtWidgets.QHBoxLayout(self)
        Layout.setContentsMargins(0, 0, 0, 0)

        # 左侧标签
        self.Label = QtWidgets.QLabel(LabelText)

        # 中间文本显示区域
        self.PathLabel = QtWidgets.QLabel("(暂无图片)")
        self.PathLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.PathLabel.setStyleSheet("background-color: #f0f0f0; padding: 2px;")

        # 按钮：选择
        self.SelectButton = QtWidgets.QPushButton("...")
        self.SelectButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.SelectButton.clicked.connect(self._OnSelectImage)

        # 按钮：删除
        self.DeleteButton = QtWidgets.QPushButton("x")
        self.DeleteButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.DeleteButton.clicked.connect(self._OnDeleteImage)

        # 添加到布局
        Layout.addWidget(self.Label)
        Layout.addWidget(self.PathLabel, stretch=1)
        Layout.addWidget(self.SelectButton)
        Layout.addWidget(self.DeleteButton)

    def SetText(self, Text):
        """设置路径文本"""
        self.PathLabel.setText(Text)

    def GetText(self):
        """获取当前路径文本"""
        return self.PathLabel.text()

    def SetOnSelect(self, Callback):
        """设置选择按钮的回调"""
        self.OnSelectCallback = Callback

    def SetOnDelete(self, Callback):
        """设置删除按钮的回调"""
        self.OnDeleteCallback = Callback

    def _OnSelectImage(self):
        if self.OnSelectCallback:
            self.OnSelectCallback()

    def _OnDeleteImage(self):
        if self.OnDeleteCallback:
            self.OnDeleteCallback()
