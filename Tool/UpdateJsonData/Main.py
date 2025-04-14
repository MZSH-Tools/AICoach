from PySide2 import QtWidgets
from Widget.QuestionWidget import QuestionWidget
from Widget.ParsingWidget import ParsingWidget
import os, json, sys, shutil

class SelectPathDialog(QtWidgets.QDialog):
    def __init__(self, DefaultJsonPath, DefaultImageDir):
        super().__init__()
        self.setWindowTitle("选择题库路径")
        self.JsonPath = os.path.abspath(DefaultJsonPath)
        self.ImageDir = os.path.abspath(DefaultImageDir)

        Layout = QtWidgets.QFormLayout(self)

        self.JsonPathEdit = QtWidgets.QLineEdit(self.JsonPath)
        JsonBrowse = QtWidgets.QPushButton("浏览")
        JsonBrowse.clicked.connect(self.SelectJsonPath)
        JsonLayout = QtWidgets.QHBoxLayout()
        JsonLayout.addWidget(self.JsonPathEdit)
        JsonLayout.addWidget(JsonBrowse)
        Layout.addRow("题库 JSON 文件：", JsonLayout)

        self.ImageDirEdit = QtWidgets.QLineEdit(self.ImageDir)
        ImgBrowse = QtWidgets.QPushButton("浏览")
        ImgBrowse.clicked.connect(self.SelectImageDir)
        ImgLayout = QtWidgets.QHBoxLayout()
        ImgLayout.addWidget(self.ImageDirEdit)
        ImgLayout.addWidget(ImgBrowse)
        Layout.addRow("图片目录路径：", ImgLayout)

        BtnBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        BtnBox.accepted.connect(self.accept)
        BtnBox.rejected.connect(self.reject)
        Layout.addRow(BtnBox)

        self.setLayout(Layout)

    def SelectJsonPath(self):
        Path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择 JSON 文件", self.JsonPath, "JSON 文件 (*.json)")
        if Path:
            self.JsonPathEdit.setText(os.path.abspath(Path))

    def SelectImageDir(self):
        Dir = QtWidgets.QFileDialog.getExistingDirectory(self, "选择图片目录", self.ImageDir)
        if Dir:
            self.ImageDirEdit.setText(os.path.abspath(Dir))

    def GetPaths(self):
        return os.path.abspath(self.JsonPathEdit.text()), os.path.abspath(self.ImageDirEdit.text())


App = QtWidgets.QApplication()
DefaultDir = os.path.dirname(os.path.abspath(__file__))
DefaultJsonPath = os.path.join(DefaultDir, "../../Data/QuestionBank.json")
DefaultImageDir = os.path.join(DefaultDir, "../../Assets/Images")

Dialog = SelectPathDialog(DefaultJsonPath, DefaultImageDir)
if Dialog.exec_() != QtWidgets.QDialog.Accepted:
    sys.exit(0)
JsonPath, OutputImageDir = Dialog.GetPaths()
FileDir = os.path.dirname(os.path.abspath(__file__))

try:
    with open(JsonPath, "r", encoding="utf-8-sig") as f:
        JsonData = json.load(f)
        Questions = JsonData.get("题库", [])
        PublicParsingLibrary = JsonData.get("公共解析库", [])
except Exception as e:
    print(f"读取 JSON 文件失败：{str(e)}")
    sys.exit(1)

def SaveQuestions(NewQuestions):
    JsonData["题库"] = NewQuestions
    print("[保存触发] 当前题库数量：", len(NewQuestions))
    try:
        with open(JsonPath, "w", encoding="utf-8") as f:
            json.dump(JsonData, f, ensure_ascii=False, indent=2)
        print("题库已保存")
    except Exception as e:
        print(f"保存 JSON 文件失败：{e}")

def SavePublicParsingLibrary(NewList):
    JsonData["公共解析库"] = NewList
    try:
        with open(JsonPath, "w", encoding="utf-8") as f:
            json.dump(JsonData, f, ensure_ascii=False, indent=2)
        print("公共解析库已保存")
    except Exception as e:
        print(f"保存 JSON 文件失败：{e}")

def OnImageChange(SetName, OldFileName, SourcePath):
    """
    图片处理统一函数：
    - SetName: 新图名称（不含扩展名）
    - OldFileName: 原图文件名（含扩展名）
    - SourcePath: 新图片路径，若为空表示清空
    """
    if OldFileName:
        OldPath = os.path.join(OutputImageDir, OldFileName)
        if os.path.exists(OldPath):
            os.remove(OldPath)

    if not SourcePath:
        return ""

    Ext = os.path.splitext(SourcePath)[1]
    NewFileName = f"{SetName}{Ext}"
    TargetPath = os.path.join(OutputImageDir, NewFileName)
    try:
        shutil.copy(SourcePath, TargetPath)
    except Exception as e:
        print(f"图片复制失败: {e}")
        return ""

    return NewFileName


Window = QtWidgets.QMainWindow()
Window.setWindowTitle("题库数据更新程序")

Screen = App.primaryScreen().geometry()
Width = int(Screen.width() * 0.8)
Height = int(Screen.height() * 0.8)
Left = (Screen.width() - Width) // 2
Top = (Screen.height() - Height) // 2
Window.setGeometry(Left, Top, Width, Height)

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
            Stack.setCurrentIndex(PageIndex)

def InitWidgetMap():
    return {
        "题库": QuestionWidget(Questions, OnUpdateCallback=SaveQuestions, OnImageAdd=OnImageChange),
        "公共解析库": ParsingWidget(PublicParsingLibrary, OnUpdate=SavePublicParsingLibrary)
    }

WidgetMap = InitWidgetMap()
ButtonList = []
CurPageIndex = -1

for Index, (Name, Widget) in enumerate(WidgetMap.items()):
    Button = QtWidgets.QPushButton(Name)
    Button.setCheckable(True)
    Button.setMinimumWidth(100)
    Button.clicked.connect(lambda checked=False, i=Index: ChangePage(i))
    ButtonList.append(Button)
    TagLayout.addWidget(Button)
    Stack.addWidget(Widget)

TagLayout.addStretch()
ChangePage(0)

Window.show()
App.exec_()
