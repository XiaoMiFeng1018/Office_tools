import os
import shutil
import re
import pdfplumber
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# ====================== 核心代码（完全不变） ======================
def get_invoice_number(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""

        patterns = [
            re.compile(r"发票号码\s*[:：]\s*(\d{21})"),
            re.compile(r"发票号\s*[:：]\s*(\d{21})"),
            re.compile(r"发票号码\s*(\d{21})"),
            re.compile(r"发票号码\s*[:：]\s*(\d+)"),
        ]

        for pat in patterns:
            match = pat.search(text)
            if match:
                return match.group(1).strip()

        return None
    except Exception as e:
        print(f"⚠️ 读取失败: {e}")
        return None

def clear_output_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except:
                pass

# ====================== 界面增强：支持 文件 + 文件夹 ======================
class InvoiceTool:
    def __init__(self, root):
        self.root = root
        self.root.title("发票重命名工具（支持文件/文件夹）")
        self.root.geometry("680x550")

        # 输入方式选择
        tk.Label(root, text="选择输入方式：", font=("微软雅黑",11)).place(x=20,y=20)
        self.input_mode = tk.StringVar(value="folder")
        tk.Radiobutton(root, text="📁 导入文件夹", variable=self.input_mode, value="folder", font=("微软雅黑",10)).place(x=150,y=20)
        tk.Radiobutton(root, text="📄 导入单个/多个文件", variable=self.input_mode, value="file", font=("微软雅黑",10)).place(x=320,y=20)

        # 路径
        tk.Label(root, text="源路径：", font=("微软雅黑",10)).place(x=20,y=60)
        self.source_path = tk.StringVar()
        tk.Entry(root, textvariable=self.source_path, width=70).place(x=20,y=90)
        tk.Button(root, text="浏览", command=self.choose_source, width=8).place(x=580,y=88)

        # 输出
        tk.Label(root, text="导出文件夹：", font=("微软雅黑",10)).place(x=20,y=130)
        self.output_path = tk.StringVar()
        tk.Entry(root, textvariable=self.output_path, width=70).place(x=20,y=160)
        tk.Button(root, text="浏览", command=self.choose_output, width=8).place(x=580,y=158)

        # 开始按钮
        tk.Button(root, text="开始处理", command=self.start_run, bg="#2196F3", fg="white",
                  width=25, height=2, font=("微软雅黑",12)).place(x=200,y=210)

        # 日志
        self.log = scrolledtext.ScrolledText(root, width=80, height=20)
        self.log.place(x=20,y=280)

    # 选择来源：自动根据模式选 文件夹 或 文件
    def choose_source(self):
        if self.input_mode.get() == "folder":
            path = filedialog.askdirectory(title="选择发票文件夹")
        else:
            path = filedialog.askopenfilenames(title="选择PDF文件", filetypes=[("PDF文件", "*.pdf")])

        if path:
            self.source_path.set(str(path))

    def choose_output(self):
        path = filedialog.askdirectory(title="选择保存文件夹")
        if path:
            self.output_path.set(path)

    def print_log(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.root.update()

    # 处理逻辑：兼容 文件 / 文件夹
    def start_run(self):
        source = self.source_path.get()
        output_dir = self.output_path.get()

        if not source or not output_dir:
            messagebox.showerror("错误", "请选择源路径和导出文件夹！")
            return

        self.print_log("="*60)
        self.print_log("开始处理...")
        self.print_log("="*60)

        clear_output_folder(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        pdf_list = []

        # 解析来源
        if self.input_mode.get() == "folder":
            folder = source
            for f in os.listdir(folder):
                if f.lower().endswith(".pdf"):
                    pdf_list.append(os.path.join(folder, f))
        else:
            try:
                # 多个文件格式
                files = eval(source)
                pdf_list = list(files)
            except:
                pdf_list = [source]

        # 处理
        for path in pdf_list:
            if not os.path.exists(path):
                continue
            filename = os.path.basename(path)
            invoice_no = get_invoice_number(path)

            if invoice_no:
                new_name = f"{invoice_no}.pdf"
                new_path = os.path.join(output_dir, new_name)
                shutil.copy2(path, new_path)
                self.print_log(f"✅ {filename} → {new_name}")
            else:
                self.print_log(f"❌ 无法识别发票号：{filename}")

        self.print_log("\n🎉 全部处理完成！")
        messagebox.showinfo("完成", "发票重命名已完成！")

if __name__ == "__main__":
    root = tk.Tk()
    InvoiceTool(root)
    root.mainloop()
