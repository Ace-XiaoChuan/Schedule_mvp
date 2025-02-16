import tkinter as tk
from tkinter import ttk  # import不会把子模块也导进来，ttk是更现代的界面组件
from database import Database


class App:
    def __init__(self):
        # 连接数据库
        self.db = Database()
        # Tk() 是 Tkinter 库中的一个构造方法,就只创建一个根窗口
        self.window = tk.Tk()
        self.window.title("我的日程管理系统")
        self._build_basic_ui()

    def _build_basic_ui(self):
        # 暂时只添加一个按钮和标签
        label = tk.Label(self.window, text="欢迎使用日程管理系统！")
        # pack()进行布局管理，pad_y:y轴边距像素
        label.pack(pady=10)

        # 在 Tkinter 里，command=self._test_db 不加括号 是因为 我只是传递函数的**引用**，而不是立即执行它。
        # 注意是引用！！！
        # test_btn = tk.Button(self.window, text="测试按钮", command=self._test_db)
        # test_btn.pack()

        self._build_task_form()  # 加载上面那个表单
        self._build_task_list()  # 加载任务列表

    def _test_db(self):
        # 测试数据库连接
        # execute(sql, params) 方法的内部逻辑会自动填充参数，
        # Python 的数据库驱动（如 sqlite3）已经实现了这个机制。
        # 它会找到 SQL 语句中的 ?，然后从参数元组中取值填入相应位置，
        # 最终执行完整的 SQL 语句，同时避免注入攻击。此为最佳实践。
        self.db.conn.execute("INSERT INTO tasks (title, due_time) VALUES (?, ?)",
                             ("测试任务", "2025-05-20 10:00"))
        self.db.conn.commit()
        print("测试数据已插入数据库！")

    def _build_task_form(self):
        # 创建表单框架
        # fill=tk.x以横轴为标准拉伸至填充父元素
        form_frame = tk.Frame(self.window)
        form_frame.pack(pady=20, padx=20, fill=tk.X)

        # 标题输入，Label放在form_frame这个容器里，
        # grid是一个布局管理器，第一行第一列，sticky="w"，w就是west向左对齐
        tk.Label(form_frame, text="任务标题：").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(form_frame, width=30)
        self.title_entry.grid(row=0, column=1)

        # 截止时间输入
        tk.Label(form_frame, text="截止时间：").grid(row=1, column=0, sticky="w")
        self.due_entry = tk.Entry(form_frame, width=30)
        self.due_entry.grid(row=1, column=1)

        # 添加按钮
        add_btn = tk.Button(form_frame, text="添加任务", command=self._add_task)
        add_btn.grid(row=2, column=1, pady=10, sticky="e")

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
        # 创建一个框架容器,填充父元素
        self.list_frame = tk.Frame(self.window)
        # expand=True尽可能扩充
        self.list_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # 使用treeview，tasklist即任务列表，放在下面
        self.task_list = ttk.Treeview(
            self.list_frame,
            columns=("id", "title", "due_time"),
            show="headings",
            selectmode="browse"
        )
        # 配置每一列的表头
        self.task_list.heading("id", text="ID")
        self.task_list.heading("title", text="任务标题")
        self.task_list.heading("due_time", text="截止时间")

        # 设置列的宽度和对齐方式
        self.task_list.column("id", width=50, anchor="center")  # anchor居中
        self.task_list.column("title", width=200)
        self.task_list.column("due_time", width=150)

        # 将列表放入界面
        self.task_list.pack(fill=tk.BOTH, expand=True)

        # 立即加载一次数据
        self._refresh_task_list()

    def _refresh_task_list(self):
        """从数据库重新加载数据并更新列表"""
        # 清空现有数据
        for item in self.task_list.get_children():
            self.task_list.delete(item)

        # 从数据库读取数据
        cursor = self.db.conn.execute("SELECT id, title, due_time FROM tasks ORDER BY due_time")
        for row in cursor:
            # 插入到列表末尾
            self.task_list.insert("", tk.END, values=row)


if __name__ == "__main__":
    app = App()
    app.window.mainloop()
