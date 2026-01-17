import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    plt.rcParams["font.sans-serif"] = [
        "Arial Unicode MS",
        "PingFang SC",
        "Heiti TC",
        "SimHei",
        "Microsoft YaHei",
        "sans-serif",
    ]
    plt.rcParams["axes.unicode_minus"] = False
except Exception:
    plt = None
    FigureCanvasTkAgg = None

from .config import DATA_FILE
from .core import (
    describe_distribution,
    describe_drawdown_distribution,
    describe_win_rate,
    parse_rr_input,
    run_monte_carlo,
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("交易盈亏比蒙特卡洛模拟")
        self.geometry("1360x960")
        self.last_totals = None
        self.last_drawdowns = None
        self.fig = None
        self.canvas = None
        self.history_entries = []
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(top_frame, text="历史盈亏比数据（用逗号或空格分隔，单位R）:").pack(anchor="w")
        self.text_rr = tk.Text(top_frame, height=8)
        self.text_rr.pack(fill=tk.X, pady=5)

        history_frame = tk.Frame(top_frame)
        history_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        tk.Label(history_frame, text="历史记录（最多10条）：").pack(anchor="w")
        self.history_list = tk.Listbox(history_frame, height=5)
        self.history_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=2)
        history_scroll_x = tk.Scrollbar(history_frame, orient=tk.HORIZONTAL, command=self.history_list.xview)
        history_scroll_x.pack(side=tk.TOP, fill=tk.X)
        self.history_list.configure(xscrollcommand=history_scroll_x.set)
        load_button = tk.Button(history_frame, text="载入选中", command=self.on_load_selected)
        load_button.pack(anchor="e", pady=2)

        params_frame = tk.Frame(self)
        params_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(params_frame, text="每次模拟的交易笔数:").grid(row=0, column=0, sticky="w")
        self.entry_trades = tk.Entry(params_frame)
        self.entry_trades.grid(row=0, column=1, padx=5)
        self.entry_trades.insert(0, "100")

        tk.Label(params_frame, text="模拟次数:").grid(row=0, column=2, sticky="w")
        self.entry_runs = tk.Entry(params_frame)
        self.entry_runs.grid(row=0, column=3, padx=5)
        self.entry_runs.insert(0, "1000")

        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        run_button = tk.Button(button_frame, text="运行模拟", command=self.on_run)
        run_button.pack(side=tk.LEFT)

        clear_button = tk.Button(button_frame, text="清空结果", command=self.on_clear)
        clear_button.pack(side=tk.LEFT, padx=5)

        save_button = tk.Button(button_frame, text="保存数据", command=self.on_save)
        save_button.pack(side=tk.LEFT, padx=5)

        # 使用 Notebook 实现标签页
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: 统计报告
        self.tab_report = tk.Frame(self.notebook)
        self.notebook.add(self.tab_report, text="统计报告")
        
        tk.Label(self.tab_report, text="模拟结果统计（单位R）:").pack(anchor="w", padx=5, pady=5)
        self.text_result = tk.Text(self.tab_report)
        self.text_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 2: 分布图表
        self.tab_chart = tk.Frame(self.notebook)
        self.notebook.add(self.tab_chart, text="分布图表")

    def on_run(self):
        rr_text = self.text_rr.get("1.0", tk.END).strip()
        if not rr_text:
            messagebox.showerror("错误", "请先输入历史盈亏比数据")
            return
        try:
            rr_list = parse_rr_input(rr_text)
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            return
        except Exception:
            messagebox.showerror("错误", "盈亏比数据格式不正确，请检查输入")
            return
        try:
            trades_per_run = int(self.entry_trades.get())
            num_runs = int(self.entry_runs.get())
        except ValueError:
            messagebox.showerror("错误", "交易笔数和模拟次数必须为整数")
            return
        try:
            totals, drawdowns = run_monte_carlo(rr_list, trades_per_run, num_runs)
            summary_main = describe_distribution(totals)
            summary_win = describe_win_rate(rr_list, totals)
            summary_dd = describe_drawdown_distribution(drawdowns)
            summary = summary_main + "\n\n" + summary_win + "\n" + summary_dd
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            return
        except Exception:
            messagebox.showerror("错误", "模拟过程中发生未知错误")
            return
        self.last_totals = totals
        self.last_drawdowns = drawdowns
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert(tk.END, summary)
        
        # 自动更新图表
        self.update_chart()

    def update_chart(self):
        if plt is None:
            return 
            
        if not self.last_totals or not self.last_drawdowns:
            return

        # 清除旧图表
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            plt.close(self.fig)

        try:
            # 创建新图表
            self.fig, axes = plt.subplots(1, 2, figsize=(12, 6), dpi=120)
            ax1 = axes[0]
            ax2 = axes[1]

            # 图1：最终盈亏
            n1, bins1, _ = ax1.hist(self.last_totals, bins=30, density=True, alpha=0.6)
            centers1 = 0.5 * (bins1[:-1] + bins1[1:])
            ax1.plot(centers1, n1, "-")
            ax1.set_title("最终盈亏R分布")
            ax1.set_xlabel("最终盈亏R")
            ax1.set_ylabel("概率密度")

            # 图2：最大回撤
            n2, bins2, _ = ax2.hist(self.last_drawdowns, bins=30, density=True, alpha=0.6)
            centers2 = 0.5 * (bins2[:-1] + bins2[1:])
            ax2.plot(centers2, n2, "-")
            ax2.set_title("最大回撤分布")
            ax2.set_xlabel("最大回撤R")
            ax2.set_ylabel("概率密度")
            
            self.fig.tight_layout()

            # 嵌入到 Tkinter
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_chart)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("错误", f"绘制图形时发生错误: {str(e)}")

    def on_clear(self):
        self.text_result.delete("1.0", tk.END)
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
            if self.fig:
                plt.close(self.fig)
                self.fig = None

    def load_data(self):
        self.history_entries = []
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            entries = []
            if isinstance(data, dict):
                if "entries" in data and isinstance(data["entries"], list):
                    for item in data["entries"]:
                        if isinstance(item, str):
                            entries.append(item)
                        elif isinstance(item, dict) and "rr_text" in item:
                            entries.append(item["rr_text"])
                elif "rr_text" in data:
                    entries.append(data["rr_text"])
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, str):
                        entries.append(item)
            self.history_entries = [{"rr_text": t} for t in entries[:10]]
            self.refresh_history_list()
            if self.history_entries:
                rr_text = self.history_entries[0]["rr_text"]
                self.text_rr.delete("1.0", tk.END)
                self.text_rr.insert(tk.END, rr_text)
        except Exception:
            pass

    def save_data(self):
        rr_text = self.text_rr.get("1.0", tk.END).strip()
        if not rr_text:
            messagebox.showerror("错误", "没有可保存的数据")
            return False
        entries = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    if "entries" in data and isinstance(data["entries"], list):
                        for item in data["entries"]:
                            if isinstance(item, str):
                                entries.append(item)
                            elif isinstance(item, dict) and "rr_text" in item:
                                entries.append(item["rr_text"])
                    elif "rr_text" in data:
                        entries.append(data["rr_text"])
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, str):
                            entries.append(item)
            except Exception:
                entries = []
        new_entries = [rr_text]
        for item in entries:
            if item != rr_text:
                new_entries.append(item)
        new_entries = new_entries[:10]
        data = {"entries": new_entries}
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.history_entries = [{"rr_text": t} for t in new_entries]
            self.refresh_history_list()
            return True
        except Exception as e:
            messagebox.showerror("错误", f"保存数据失败: {str(e)}")
            return False

    def on_save(self):
        if self.save_data():
            messagebox.showinfo("成功", "数据已保存")

    def refresh_history_list(self):
        if not hasattr(self, "history_list"):
            return
        self.history_list.delete(0, tk.END)
        for index, entry in enumerate(self.history_entries):
            rr_text = entry.get("rr_text", "")
            preview = rr_text.replace("\n", " ")
            label = f"{index + 1}: {preview}"
            self.history_list.insert(tk.END, label)

    def on_load_selected(self):
        if not hasattr(self, "history_list"):
            return
        selection = self.history_list.curselection()
        if not selection:
            messagebox.showerror("错误", "请先在历史记录中选择一条数据")
            return
        index = selection[0]
        if index < 0 or index >= len(self.history_entries):
            return
        rr_text = self.history_entries[index].get("rr_text", "")
        self.text_rr.delete("1.0", tk.END)
        self.text_rr.insert(tk.END, rr_text)
