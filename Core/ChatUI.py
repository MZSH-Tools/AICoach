import tkinter as tk
from tkinter import messagebox
from queue import Queue
from PIL import Image, ImageTk  # 添加 PIL 用于显示图片


# ChatUI 类负责构建聊天界面，显示题目内容、接收用户输入，并触发 AI 回调，是用户交互的核心窗口。
class ChatUI:
    def __init__(self):
        self.Root = tk.Tk()
        self.Root.title("AI 教练 Demo")
        self.Root.configure(bg="white")
        self.Root.minsize(400, 500)

        # 使用垂直分区布局，TopFrame + BottomFrame
        self.MainFrame = tk.Frame(self.Root, bg="white")
        self.MainFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.InitGeometry(960, 700)
        self.OnAIRequested = None

        self.UserBubbleColor = "#d4edda"
        self.BotBubbleColor = "#e0e0e0"
        self.UserAvatarColor = "#a2d5ac"
        self.BotAvatarColor = "#bbb"

        # 创建一个上层 Frame 分隔聊天区和输入区
        self.TopFrame = tk.Frame(self.MainFrame, bg="white")
        self.TopFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.Canvas = tk.Canvas(self.TopFrame, bg="white", highlightthickness=0, yscrollincrement=5)
        self.ChatFrame = tk.Frame(self.Canvas, bg="white")
        self.Scrollbar = tk.Scrollbar(self.TopFrame, command=self.Canvas.yview)
        self.Canvas.configure(yscrollcommand=self.Scrollbar.set)

        self.Scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.Canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ChatWindow = self.Canvas.create_window((0, 0), window=self.ChatFrame, anchor='nw', tags="chat_frame")
        self.ChatFrame.bind("<Configure>", lambda e: [
            self.Canvas.configure(scrollregion=self.Canvas.bbox("all")),
            self.Canvas.itemconfig(self.ChatWindow, width=self.Canvas.winfo_width())
        ])

        self.MsgIndex = 0
        self.ImageRefs = []

        Separator = tk.Frame(self.Root, height=1, bg="#ddd")
        Separator.pack(fill=tk.X, padx=10, pady=(5, 0))

        self.BottomFrame = tk.Frame(self.MainFrame, bg="white")
        self.BottomFrame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.HintLabel = tk.Label(self.BottomFrame, text="请输入：", bg="white", anchor="w", font=("微软雅黑", 10))
        self.HintLabel.pack(anchor="w")

        self.InputText = tk.Text(
            self.BottomFrame,
            height=4,
            wrap="word",
            font=("微软雅黑", 10),
            bd=1,
            relief="solid"
        )
        self.InputText.pack(fill=tk.X, pady=(5, 0))

        self.InputText.bind("<Return>", self.OnEnter)
        self.InputText.bind("<Shift-Return>", self.OnShiftEnter)

        self.InputQueue = Queue()
        self.Processing = False
        self.Placeholders = []

    def InitGeometry(self, Width, Height):
        ScreenWidth = self.Root.winfo_screenwidth()
        ScreenHeight = self.Root.winfo_screenheight()
        X = (ScreenWidth - Width) // 2
        Y = (ScreenHeight - Height) // 2
        self.Root.geometry(f'{Width}x{Height}+{X}+{Y}')

    @staticmethod
    def CreateColorAvatar(color):
        size = 40
        from PIL import ImageDraw
        img = Image.new("RGB", (size, size), color)
        photo = ImageTk.PhotoImage(img)
        return photo

    def InsertMessage(self, sender, message):
        self.MsgIndex += 1
        Container = tk.Frame(self.ChatFrame, bg="white")
        Container.grid(row=self.MsgIndex, column=0, sticky="w", padx=10, pady=5)

        AvatarFrame = tk.Frame(Container, bg="white", width=40, height=40)
        AvatarFrame.grid(row=0, column=0, sticky="nw")

        AvatarColor = self.UserAvatarColor if sender == "user" else self.BotAvatarColor
        AvatarImage = self.CreateColorAvatar(AvatarColor)
        AvatarLabel = tk.Label(AvatarFrame, image=AvatarImage, bg="white", bd=0)
        AvatarLabel.image = AvatarImage
        AvatarLabel.pack()

        BubbleColor = self.UserBubbleColor if sender == "user" else self.BotBubbleColor
        TextLabel = tk.Label(
            Container,
            text=message,
            bg=BubbleColor,
            fg="black",
            wraplength=500,
            justify="left",
            padx=10,
            pady=10,
            font=("微软雅黑", 10),
        )
        TextLabel.grid(row=0, column=1, sticky="w", padx=(6, 0))

        # 移除无效语法或替换为滚动到底部（可选）
        self.Root.after(10, lambda: self.Canvas.yview_moveto(1.0))

        return Container

    def InsertPlaceholder(self, text="已加入队列，等待中..."):
        Placeholder = self.InsertMessage("ai", text)
        self.Placeholders.append(Placeholder)
        return Placeholder

    def SetInputEnabled(self, Enabled: bool):
        State = tk.NORMAL if Enabled else tk.DISABLED
        self.InputText.config(state=State)

    def OnEnter(self, event):
        UserInput = self.InputText.get("1.0", tk.END).strip()
        if not UserInput:
            messagebox.showwarning("提示", "请输入内容")
            return "break"

        self.InputText.delete("1.0", tk.END)
        self.InsertMessage("user", UserInput)
        Placeholder = self.InsertPlaceholder("已加入队列，等待中...")

        self.InputQueue.put((UserInput, Placeholder))
        self.TryProcessNext()

        return "break"

    def OnShiftEnter(self, event):
        self.InputText.insert(tk.INSERT, "\n")
        return "break"

    def TryProcessNext(self):
        if self.Processing or self.InputQueue.empty():
            return

        self.Processing = True
        UserInput, Placeholder = self.InputQueue.get()
        self.UpdatePlaceholder(Placeholder, "AI 教练正在思考中...")

        if self.OnAIRequested:
            self.OnAIRequested(UserInput, Placeholder)

    def UpdatePlaceholder(self, PlaceholderContainer, NewText):
        for widget in PlaceholderContainer.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(text=NewText)

    def CompleteReply(self, AIResponse, Placeholder):
        self.UpdatePlaceholder(Placeholder, AIResponse)
        self.Processing = False
        self.TryProcessNext()

    def Run(self):
        self.Root.mainloop()

    def DisplayMessageBlocks(self, Blocks):
        Texts = []
        Images = []
        for Block in Blocks:
            if Block.startswith("[TEXT]"):
                Text = Block.replace("[TEXT]", "").strip()
                Texts.append(Text)
            elif Block.startswith("[IMAGE]"):
                Path = Block.replace("[IMAGE]", "").strip()
                Images.append(Path)

        self.MsgIndex += 1
        Container = tk.Frame(self.ChatFrame, bg="white")
        Container.grid(row=self.MsgIndex, column=0, sticky="w", padx=10, pady=5)

        AvatarFrame = tk.Frame(Container, bg="white", width=40, height=40)
        AvatarFrame.grid(row=0, column=0, sticky="nw")

        AvatarImage = self.CreateColorAvatar(self.BotAvatarColor)
        AvatarLabel = tk.Label(AvatarFrame, image=AvatarImage, bg="white", bd=0)
        AvatarLabel.image = AvatarImage
        AvatarLabel.pack()

        BubbleColor = self.BotBubbleColor
        BubbleFrame = tk.Frame(Container, bg=BubbleColor)
        BubbleFrame.grid(row=0, column=1, sticky="w", padx=(6, 0))

        for Text in Texts:
            Label = tk.Label(BubbleFrame, text=Text, bg=BubbleColor, fg="black", wraplength=500, justify="left",
                             anchor="w", font=("微软雅黑", 10), padx=10, pady=4)
            Label.pack(anchor="w")

        for Path in Images:
            try:
                ImageObj = Image.open(Path).convert("RGB").resize((300, 200))
                Photo = ImageTk.PhotoImage(ImageObj)
                self.ImageRefs.append(Photo)
                Label = tk.Label(BubbleFrame, image=Photo, bg=BubbleColor)
                Label.image = Photo
                Label.pack(anchor="w", pady=5)
            except Exception as Error:
                print(f"[图片加载失败] {Path}: {Error}")


if __name__ == "__main__":
    App = ChatUI()


    def MockAI(UserInput, Placeholder):
        Response = f"[TEXT] 您刚才说的是：{UserInput}"
        App.Root.after(1000, lambda: App.CompleteReply(Response, Placeholder))


    App.OnAIRequested = MockAI
    App.Run()
