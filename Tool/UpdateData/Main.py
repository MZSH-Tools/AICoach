from PySide2 import QtWidgets

App = QtWidgets.QApplication()
Window = QtWidgets.QMainWindow()

Window.setWindowTitle("数据更新程序")
Screen = App.primaryScreen().geometry()
Width = Screen.width()
Height = Screen.height()
Window.setGeometry(Width//4, Height//4, Width//2, Height//2)

CentralWidget = QtWidgets.QWidget()
Window.setCentralWidget(CentralWidget)
MainLayout = QtWidgets.QVBoxLayout(CentralWidget)

TagLayout = QtWidgets.QHBoxLayout()
MainLayout.addLayout(TagLayout, stretch=0)
Stack = QtWidgets.QStackedWidget()
MainLayout.addWidget(Stack, stretch=1)

def ChangePage(PageIndex):
    global CurPageIndex, ButtonList
    if CurPageIndex != PageIndex:
        if 0 <= CurPageIndex < len(ButtonList):
            ButtonList[CurPageIndex].setChecked(False)
        if 0 <= PageIndex < len(ButtonList):
            ButtonList[PageIndex].setChecked(True)
            CurPageIndex = PageIndex
            print(f"ChangePage {CurPageIndex}")

PageMap = {
            "首页": QtWidgets.QWidget(),#HomeWidget(),
            "设置": QtWidgets.QWidget(),#SettingsWidget(),
            "关于": QtWidgets.QWidget()#AboutWidget()
        }
ButtonList = []
CurPageIndex = -1

for Index, (Name, Widget) in enumerate(PageMap.items()):
    Button = QtWidgets.QPushButton(Name)
    Button.setCheckable(True)
    Button.clicked.connect(lambda checked=False, i=Index: Stack.setCurrentIndex(i))
    ButtonList.append(Button)
    TagLayout.addWidget(Button)
    Stack.addWidget(Widget)

TagLayout.addStretch()
Stack.currentChanged.connect(ChangePage)
ChangePage(Stack.currentIndex())

Window.show()
App.exec_()