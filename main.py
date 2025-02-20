import sqlite3
import tkinter as tk
from tkinter import ttk  # import不会把子模块也导进来，ttk是更现代的界面组件
from database import Database
import datetime
import tkinter.messagebox as messagebox


class App:
    def __init__(self):
        # 连接数据库
        self.db = Database()
        # Tk() 是 Tkinter 库中的一个构造方法,就只创建一个根窗口
        self.window = tk.Tk()
        self.window.title("我的日程管理系统")
        self._build_basic_ui()
        self._build_auto_timer()
        self.current_task = None

    def _build_basic_ui(self):
        label = tk.Label(self.window, text="欢迎使用日程管理系统！")
        label.pack(pady=10)

        self._build_task_form()  # 加载上面那个表单
        self._build_task_list()  # 加载下面任务列表

    def _build_task_form(self):
        # 创建表单框架
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=20, padx=20, fill=tk.X)

        # 第一项：任务分类（要有一个下拉菜单）。
        tk.Label(form_frame, text="任务分类:").grid(row=0, column=0, sticky="w")
        self.category_combo = ttk.Combobox(form_frame, values=["工作", "休闲", "睡眠"], state="readonly")
        self.category_combo.grid(row=0, column=1)
        self.category_combo.current(0)

        # 第二项：任务标题
        tk.Label(form_frame, text="任务标题：").grid(row=1, column=0, sticky="w")
        self.title_entry = tk.Entry(form_frame, width=30)
        self.title_entry.grid(row=1, column=1)

        # 第三项：开始时间
        tk.Label(form_frame, text="开始时间：").grid(row=2, column=0, sticky="w")
        self.start_entry = tk.Entry(form_frame, width=20)
        self.start_entry.grid(row=2, column=1, sticky="w")

        # 第四项：结束时间
        tk.Label(form_frame, text="结束时间：").grid(row=3, column=0, sticky="w")
        self.end_entry = tk.Entry(form_frame, width=20)
        self.end_entry.grid(row=3, column=1, sticky="w")

        # 添加手动任务按钮
        manual_btn = tk.Button(form_frame, text="添加手动任务", command=self._add_manual_task)
        manual_btn.grid(row=4, column=1, pady=10, sticky="e")

    def _add_manual_task(self):
        category = self.category_combo.get()
        title = self.title_entry.get()
        start_time = self.start_entry.get()
        end_time = self.end_entry.get()

        # 简单验证
        # 在 C/C++/Java 等语言中，return 必须显式返回值（或声明为 void 函数）。
        # 在 Python 中，函数默认返回 None，因此 return 可单独使用。
        if not title or not start_time:
            tk.messagebox.showerror("错误", "任务标题和开始时间不能为空！")
            return

        try:
            # 验证时间格式
            # datetime的datetime的strptime时间模板太多了，链接记于此，时时查阅：
            # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
            datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if end_time:
                datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

            # 插入数据库
            self.db.conn.execute(
                """INSERT INTO tasks 
                (title, category, start_time, end_time, is_auto) 
                VALUES (?, ?, ?, ?, ?)""",
                (title, category, start_time, end_time, 0)  # is_auto=0 表示手动任务
            )
            self.db.conn.commit()

            # 清空输入框
            self.title_entry.delete(0, tk.END)
            self.start_entry.delete(0, tk.END)
            self.end_entry.delete(0, tk.END)

            # 刷新任务列表
            self._refresh_task_list()

        except ValueError:
            tk.messagebox.showerror("错误", "时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式！")
            return
        except sqlite3.Error as e:
            tk.messagebox.showerror("错误", f"数据库错误: {e}")
            return

    def _build_auto_timer(self):
        timer_frame = tk.Frame(self.window)
        timer_frame.pack(pady=10, fill=tk.X)

        # 分类选择
        tk.Label(timer_frame, text="任务分类：").pack(side=tk.LEFT)
        self.auto_category = ttk.Combobox(timer_frame,
                                          values=["工作", "休闲", "睡眠"],
                                          state="readonly")
        self.auto_category.pack(side=tk.LEFT)
        self.auto_category.current(0)

        # 开始/结束计时按钮：
        self.start_btn = tk.Button(timer_frame, text="开始任务",
                                   command=self._start_auto_task)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn = tk.Button(timer_frame, text="停止任务",
                                  state=tk.DISABLED,
                                  command=self._stop_auto_task)
        self.stop_btn.pack(side=tk.LEFT)

    def _start_auto_task(self):
        # 记录开始时间
        self.current_task = {
            "title": "自动记录任务",
            "category": self.auto_category.get(),
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_auto": 1
        }
        # 更新按钮状态
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.auto_category.config(state=tk.DISABLED)

    def _stop_auto_task(self):
        if self.current_task:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 插入数据库
            self.db.conn.execute(
                """INSERT INTO tasks
                (title,category,start_time,end_time,is_auto)
                VALUES (?,?,?,?,?,)""",
                (self.current_task["title"],
                 self.current_task["category"],
                 self.current_task["start_time"],
                 end_time,
                 self.current_task["is_auto"])
            )
            self.db.conn.commit()

            # 重置状态
            self.current_task = None
            # 三种状态：
            # tk.NORMAL：控件可用，用户可以交互。
            # tk.DISABLED：控件不可用，用户无法交互。
            # tk.ACTIVE：控件被激活，通常用于显示控件的激活状态
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.auto_category.config(state=tk.NORMAL)
            self._refresh_task_list()

    def _add_task(self):
        title = self.title_entry.get()
        due_time = self.due_entry.get()

        if title:  # 简单验证
            self.db.insert_task(title, due_time)
            self.title_entry.delete(0, tk.END)  # 清空输入框
            self.due_entry.delete(0, tk.END)
            self._refresh_task_list()  # 刷新任务列表（下一步实现）

    def _build_task_list(self):
        """创建任务列表的界面组件"""
        self.list_frame = tk.Frame(self.window)
        self.list_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # 修改列的定义
        self.task_list = ttk.Treeview(
            self.list_frame,
            columns=("id", "title", "category", "start_time", "end_time", "duration"),
            show="headings",
            selectmode="browse"
        )
        # 配置表头
        columns = [
            ("id", "ID", 50),
            ("title", "任务标题", 150),
            ("category", "分类", 80),
            ("start_time", "开始时间", 150),
            ("end_time", "结束时间", 150),
            ("duration", "持续时间", 100)
        ]

        for col_id, text, width in columns:
            self.task_list.heading(col_id, text=text)
            self.task_list.column(col_id, width=width, anchor="center")

        self.task_list.pack(fill=tk.BOTH, expand=True)
        self._refresh_task_list()

    def _refresh_task_list(self):
        """从数据库重新加载数据并更新列表"""
        # 清空现有数据
        # get_children()返回所有子项，
        for item in self.task_list.get_children():
            self.task_list.delete(item)

        # 按时间从数据库读取数据
        # 关于cursor这个游标：sqlite3里，cursor就是sqlite3.Cursor类型，类似指针，
        # 使用它是因为他是可迭代对象，可以for _ in...这么用，不用纠结他是什么类型，只需要知道默认迭代返回的是元组即可
        cursor = self.db.conn.execute("""
            SELECT id, title, category, start_time, end_time,
               (strftime('%s', end_time) - strftime('%s', start_time)) 
            FROM tasks 
            WHERE end_time IS NOT NULL
            ORDER BY start_time DESC
            """)
        for row in cursor:
            # ttk的insert()方法：这里补充一下方法的解释：parent=''即作为顶级节点插入
            # self.task_list.insert("", tk.END, values=row)
            duration = f"{row[5] // 3600}小时{row[5] % 3600 // 60}分钟" if row[5] else "进行中"
            self.task_list.insert("", tk.END, values=(row[0], row[1], row[2],
                                                      row[3], row[4], duration))


if __name__ == "__main__":
    app = App()
    app.window.mainloop()
