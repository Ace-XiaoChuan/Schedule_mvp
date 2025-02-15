import tkinter as tk
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

        # 在 Tkinter 里，command=self._test_db 不加括号 是因为 你在传递函数的引用，而不是立即执行它。
        # 注意是引用！！！
        test_btn = tk.Button(self.window, text="测试按钮", command=self._test_db)
        test_btn.pack()

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


if __name__ == "__main__":
    app = App()
    app.window.mainloop()
