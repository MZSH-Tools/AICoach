import tkinter as tk
from tkinter import messagebox
from queue import Queue

class ChatUI:
    def __init__(self):
        self.Root = tk.Tk()
        self.Root.title("AI 教练 Demo")
        self.Root.configure(bg="white")
        self.Root.minsize(400, 500)
        self.InitGeometry(960, 700)
        self.OnUserInput = None

        # 配色主题
        self.UserBubbleColor = "#d4edda"
        self.BotBubbleColor = "#e0e0e0"
        self.UserAvatarColor = "#a2d5ac"
        self.BotAvatarColor = "#bbb"

        # 聊天区域（滚动）
        self.Canvas = tk.Canvas(self.Root, bg="white", highlightthickness=0)
        self.ChatFrame = tk.Frame(self.Canvas, bg="white")
        self.Scrollbar = tk.Scrollbar(self.Root, command=self.Canvas.yview)
        self.Canvas.configure(yscrollcommand=self.Scrollbar.set)

        self.Scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.Canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.Canvas.create_window((0, 0), window=self.ChatFrame, anchor='nw')

        self.ChatFrame.bind("<Configure>", lambda e: self.Canvas.configure(scrollregion=self.Canvas.bbox("all")))

        self.MsgIndex = 0

        # 分隔线
        Separator = tk.Frame(self.Root, height=1, bg="#ddd")
        Separator.pack(fill=tk.X, padx=10, pady=(5, 0))

        # 底部输入区域
        self.BottomFrame = tk.Frame(self.Root, bg="white")
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

        # AI 回复排队机制
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
        AvatarCanvas = tk.Canvas(width=40, height=40, bg="white", highlightthickness=0)
        AvatarCanvas.create_rectangle(0, 0, 40, 40, fill=color, outline=color)
        return AvatarCanvas

    def InsertMessage(self, sender, message):
        self.MsgIndex += 1

        Container = tk.Frame(self.ChatFrame, bg="white")
        Container.grid(row=self.MsgIndex, column=0, sticky="w", padx=10, pady=5)

        AvatarFrame = tk.Frame(Container, bg="white", width=40, height=40)
        AvatarFrame.grid(row=0, column=0, sticky="nw")

        AvatarColor = self.UserAvatarColor if sender == "user" else self.BotAvatarColor
        AvatarCanvas = self.CreateColorAvatar(AvatarColor)
        AvatarCanvas.pack(in_=AvatarFrame)

        BubbleColor = self.UserBubbleColor if sender == "user" else self.BotBubbleColor
        TextLabel = tk.Label(
            Container,
            text=message,
            bg=BubbleColor,
            fg="black",
            wraplength=400,
            justify="left",
            padx=10,
            pady=6,
            font=("微软雅黑", 10),
        )
        TextLabel.grid(row=0, column=1, sticky="w", padx=(6, 0))

        self.Canvas.update_idletasks()
        self.Canvas.yview_moveto(1.0)
        return Container

    def InsertPlaceholder(self, Text="已加入队列，等待中..."):
        Placeholder = self.InsertMessage("ai", Text)
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

        self.Root.after(2000, lambda: self.CompleteReply(UserInput, Placeholder))

    def UpdatePlaceholder(self, PlaceholderContainer, NewText):
        for widget in PlaceholderContainer.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(text=NewText)

    def CompleteReply(self, UserInput, Placeholder):
        # 模拟 AI 回复内容
        AIResponse = f"AI 教练解析：这是对「{UserInput}」的解答示例。"
        self.UpdatePlaceholder(Placeholder, AIResponse)
        self.Processing = False
        self.TryProcessNext()

    def Run(self):
        self.Root.mainloop()


if __name__ == "__main__":
    App = ChatUI()
    App.Run()