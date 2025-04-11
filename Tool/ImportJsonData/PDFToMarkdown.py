import os
import sys
import subprocess
import importlib.util
import tkinter as Tk
from tkinter import filedialog
from pdf_craft import PDFPageExtractor, MarkDownWriter
from tqdm import tqdm

def RunPip(Args: list[str]):
    subprocess.run([sys.executable, "-m", "pip"] + Args, check=True)

def GetCurrentVersion(Pkg: str) -> str | None:
    try:
        from importlib.metadata import version
        return version(Pkg)
    except:
        return None

def HasCuda() -> bool:
    try:
        subprocess.check_output("nvidia-smi", stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def EnsureCorrectOnnxRuntime():
    Expected = "onnxruntime-gpu" if HasCuda() else "onnxruntime"
    Version = GetCurrentVersion(Expected)
    if Version == "1.21.0":
        print(f"✅ {Expected} 已是正确版本")
        return

    for Name in ("onnxruntime", "onnxruntime-gpu", "onnxruntime_gpu"):
        if importlib.util.find_spec(Name.replace("-", "_")):
            print(f"卸载：{Name}")
            RunPip(["uninstall", "-y", Name])

    print(f"📦 安装 {Expected}==1.21.0")
    RunPip(["install", f"{Expected}==1.21.0"])

def SelectPdfFile() -> str:
    Root = Tk.Tk()
    Root.withdraw()
    return filedialog.askopenfilename(
        title="选择一个 PDF 文件",
        filetypes=[("PDF 文件", "*.pdf")]
    )

def ConvertPdfToMarkdown(PdfPath: str):
    OutputMd = PdfPath.replace(".pdf", ".md")
    ImageDir = PdfPath.replace(".pdf", "_Images")
    UserHome = os.path.expanduser("~")
    ModelDir = os.path.join(UserHome, ".pdfcraft", "models")

    print(f"📁 模型缓存路径：{ModelDir}")

    Extractor = PDFPageExtractor(
        device="cuda:0" if HasCuda() else "cpu",
        model_dir_path=ModelDir
    )

    import fitz
    TotalPages = len(fitz.open(PdfPath))

    with MarkDownWriter(OutputMd, ImageDir, "utf-8") as Writer:
        for Block in tqdm(Extractor.extract(pdf=PdfPath), total=TotalPages, desc="转换中"):
            Writer.write(Block)

    print(f"\n✅ 转换完成：{OutputMd}")
    print(f"🖼️ 图片目录：{ImageDir}")


if __name__ == "__main__":
    EnsureCorrectOnnxRuntime()
    PdfFile = SelectPdfFile()
    if PdfFile:
        ConvertPdfToMarkdown(PdfFile)
    else:
        print("❌ 未选择 PDF 文件，已退出。")
