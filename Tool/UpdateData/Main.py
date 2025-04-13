from PySide2 import QtWidgets
from Widget.QuestionWidget import QuestionWidget
import os, json, sys

# 路径管理
FileDir = os.path.dirname(os.path.abspath(__file__))
JsonPath = os.path.join(FileDir, "../../Data/QuestionBank.json")
OutputImageDir = os.path.join(FileDir, "../../Assets/Images")

# 初始化数据
try:
    with open(JsonPath, "r", encoding="utf-8-sig") as f:
        JsonData = json.load(f)
        Questions = JsonData.get("题库", [])
        PublicParsingLibrary = JsonData.get("公共解析库", [])
except Exception as e:
    print(f"读取 JSON 文件失败：{str(e)}")
    sys.exit(1)

# 回调函数：保存题库内容
def SaveQuestions(NewQuestions):
    JsonData["题库"] = NewQuestions
    try:
        with open(JsonPath, "w", encoding="utf-8") as f:
            json.dump(JsonData, f, ensure_ascii=False, indent=2)
        print("题库已保存")
    except Exception as e:
        print(f"保存 JSON 文件失败：{e}")

# 初始化 UI 应用和主窗口
App = QtWidgets.QApplication()
Window = QtWidgets.QMainWindow()
Window.setWindowTitle("数据更新程序")

Screen = App.primaryScreen().geometry()
Window.setGeometry(Screen.width() // 4, Screen.height() // 4, Screen.width() // 2, Screen.height() // 2)

CentralWidget = QtWidgets.QWidget()
Window.setCentralWidget(CentralWidget)
MainLayout = QtWidgets.QVBoxLayout(CentralWidget)

# 顶部标签页按钮区和主内容区
TagLayout = QtWidgets.QHBoxLayout()
MainLayout.addLayout(TagLayout, stretch=0)
Stack = QtWidgets.QStackedWidget()
MainLayout.addWidget(Stack, stretch=1)

# 页切换函数
def ChangePage(PageIndex):
    global CurPageIndex, ButtonList
    if CurPageIndex != PageIndex:
        if 0 <= CurPageIndex < len(ButtonList):
            ButtonList[CurPageIndex].setChecked(False)
        if 0 <= PageIndex < len(ButtonList):
            ButtonList[PageIndex].setChecked(True)
            CurPageIndex = PageIndex
            print(f"切换至页面：{CurPageIndex}")

# 初始化页面组件
def InitWidgetMap():
    return {
        "题库": QuestionWidget(Questions, OnUpdateCallback=SaveQuestions),
        # "解析库": ParsingWidget(PublicParsingLibrary, OnUpdateCallback=SaveParsing),
    }

WidgetMap = InitWidgetMap()
ButtonList = []
CurPageIndex = -1

# 添加按钮与页面
for Index, (Name, Widget) in enumerate(WidgetMap.items()):
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
