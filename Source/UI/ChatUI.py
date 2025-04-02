
import tkinter as tk
from tkinter import messagebox
from queue import Queue
from PIL import Image, ImageTk
import os


class ChatUI:
    def __init__(self):
        self.Root = tk.Tk()
        self.Root.title("AI 教练 Demo")
        self.Root.configure(bg="white")
        self.Root.minsize(400, 500)

        self.MainFrame = tk.Frame(self.Root, bg="white")
        self.MainFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.InitGeometry(960, 700)
        self.OnAIRequested = None

        self.UserBubbleColor = "#d4edda"
        self.BotBubbleColor = "#e0e0e0"
        self.UserAvatarColor = "#a2d5ac"
        self.BotAvatarColor = "#bbb"

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

        self.HintLabel = tk.Label(self.BottomFrame, text="请输入：", bg="white", anchor="w", font=("微软黑", 10))
        self.HintLabel.pack(anchor="w")

        self.InputText = tk.Text(
            self.BottomFrame,
            height=4,
            wrap="word",
            font=("微软黑", 10),
            bd=1,
            relief="solid"
        )
        self.InputText.pack(fill=tk.X, pady=(5, 0))

        self.InputText.bind("<Return>", self.OnEnter)
        self.InputText.bind("<Shift-Return>", self.OnShiftEnter)

        self.InputQueue = Queue()
        self.Processing = False
        self.CurrentReplyFrame = None

    def InitGeometry(self, Width, Height):
        ScreenWidth = self.Root.winfo_screenwidth()
        ScreenHeight = self.Root.winfo_screenheight()
        X = (ScreenWidth - Width) // 2
        Y = (ScreenHeight - Height) // 2
        self.Root.geometry(f'{Width}x{Height}+{X}+{Y}')

    def CreateColorAvatar(self, Color):
        Size = 40
        from PIL import ImageDraw
        Img = Image.new("RGB", (Size, Size), Color)
        Draw = ImageDraw.Draw(Img)
        Draw.ellipse((0, 0, Size - 1, Size - 1), fill=Color)
        Photo = ImageTk.PhotoImage(Img)
        self.ImageRefs.append(Photo)
        return Photo

    def InsertMessage(self, Sender, Message):
        Container = self.BeginReplyBlock(Sender)
        self.AppendTextToReplyBlock(Message, Container)
        return Container

    def BeginReplyBlock(self, Sender="ai"):
        self.MsgIndex += 1
        Container = tk.Frame(self.ChatFrame, bg="white")
        Container.grid(row=self.MsgIndex, column=0, sticky="w", padx=10, pady=5)

        AvatarFrame = tk.Frame(Container, bg="white", width=40, height=40)
        AvatarFrame.grid(row=0, column=0, sticky="nw")

        AvatarColor = self.UserAvatarColor if Sender == "user" else self.BotAvatarColor
        AvatarImage = self.CreateColorAvatar(AvatarColor)
        AvatarLabel = tk.Label(AvatarFrame, image=AvatarImage, bg="white", bd=0)
        AvatarLabel.image = AvatarImage
        AvatarLabel.pack()

        BubbleColor = self.UserBubbleColor if Sender == "user" else self.BotBubbleColor
        ReplyFrame = tk.Frame(Container, bg=BubbleColor)
        ReplyFrame.grid(row=0, column=1, sticky="w", padx=(6, 0))
        Container._reply_frame = ReplyFrame
        self.Root.after(10, lambda: self.Canvas.yview_moveto(1.0))
        return ReplyFrame

    def AppendTextToReplyBlock(self, Text, ReplyFrame):
        Label = tk.Label(ReplyFrame, text=Text, bg=ReplyFrame["bg"], fg="black",
                         wraplength=500, justify="left", font=("微软雅黑", 10), padx=10, pady=4, anchor="w")
        Label.pack(anchor="w")

    def AppendImageToReplyBlock(self, Path, ReplyFrame):
        try:
            ImageObj = Image.open(Path).convert("RGB").resize((300, 200))
            Photo = ImageTk.PhotoImage(ImageObj)
            self.ImageRefs.append(Photo)
            Label = tk.Label(ReplyFrame, image=Photo, bg=ReplyFrame["bg"])
            Label.image = Photo
            Label.pack(anchor="w", pady=5)
        except Exception as Error:
            print(f"[图片加载失败] {Path}: {Error}")

    def OnEnter(self, Event):
        UserInput = self.InputText.get("1.0", tk.END).strip()
        if not UserInput:
            messagebox.showwarning("提示", "请输入内容")
            return "break"

        self.InputText.delete("1.0", tk.END)
        self.InsertMessage("user", UserInput)

        # 插入“排队中”的占位气泡
        Placeholder = self.BeginReplyBlock("ai")
        self.AppendTextToReplyBlock("已加入队列，等待中...", Placeholder)

        self.CurrentReplyFrame = Placeholder
        self.InputQueue.put((UserInput, Placeholder))
        self.TryProcessNext()
        return "break"

    def OnShiftEnter(self, Event):
        self.InputText.insert(tk.INSERT, "\n")
        return "break"

    def TryProcessNext(self):
        if self.Processing or self.InputQueue.empty():
            return
        self.Processing = True
        UserInput, Placeholder = self.InputQueue.get()
        self.CurrentReplyFrame = Placeholder

        # ✅ 清空旧内容并设置为“思考中...”
        for Widget in Placeholder.winfo_children():
            Widget.destroy()
        self.AppendTextToReplyBlock("AI 教练正在思考...", Placeholder)

        if self.OnAIRequested:
            self.OnAIRequested(UserInput, Placeholder)

    def AppendTokenToReply(self, Token, Placeholder):
        if not hasattr(Placeholder, "_stream_started"):
            for Widget in Placeholder.winfo_children():
                Widget.destroy()
            Placeholder._stream_started = True
            Placeholder._token_label = None

        if not hasattr(Placeholder, "_token_label") or Placeholder._token_label is None:
            Label = tk.Label(
                Placeholder,
                text=Token,
                bg=Placeholder["bg"],
                fg="black",
                wraplength=500,
                justify="left",
                anchor="w",
                font=("微软雅黑", 10),
                padx=10,
                pady=4
            )
            Label.pack(anchor="w")
            Placeholder._token_label = Label
        else:
            Current = Placeholder._token_label.cget("text")
            Placeholder._token_label.config(text=Current + Token)

        self.Canvas.update_idletasks()
        self.Canvas.yview_moveto(1.0)

    def AppendMessageBlocks(self, Blocks, Sender="ai"):
        Reply = self.BeginReplyBlock(Sender)
        for Block in Blocks:
            if Block.startswith("[TEXT]"):
                self.AppendTextToReplyBlock(Block.replace("[TEXT]", "").strip(), Reply)
            elif Block.startswith("[IMAGE]"):
                self.AppendImageToReplyBlock(Block.replace("[IMAGE]", "").strip(), Reply)
        return Reply

    def CompleteReply(self):
        self.Processing = False
        self.TryProcessNext()

    def Run(self):
        self.Root.mainloop()

if __name__ == "__main__":
    import time
    from threading import Thread

    App = ChatUI()

    def MockAI(UserInput, Placeholder):
        # 开始新回复块
        Reply = Placeholder

        def SimulateStream():
            time.sleep(1)
            # 清空旧内容（由 AppendTokenToReply 首次触发）
            for Token in "这是一个模拟的 AI 流式回复：":
                time.sleep(0.1)
                App.AppendTokenToReply(Token, Reply)

            # 模拟图文混排
            App.AppendTextToReplyBlock("下面是一个示意图：", Reply)
            App.AppendTextToReplyBlock("继续加点解释内容...", Reply)
            App.CompleteReply()

        Thread(target=SimulateStream).start()

    App.OnAIRequested = MockAI
    App.Run()

