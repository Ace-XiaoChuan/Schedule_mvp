import tkinter as tk
from tkinter import ttk


class MainView:
    # Views结构,不包含任何业务逻辑！！！
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("我的日程管理系统")
        self.current_task = None
        self._build_basic_ui()
        self._build_auto_timer()
        self.current_task = None  # 当前无正在执行的任务，
        # 这个拿来作为自动计时的flag

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

        # 调试输出
        print("✅ 表单组件创建完成")

        # 第三项：开始时间
        tk.Label(form_frame, text="开始时间：").grid(row=2, column=0, sticky="w")
        self.start_entry = tk.Entry(form_frame, width=20)
        self.start_entry.grid(row=2, column=1, sticky="w")

        # 第四项：结束时间
        tk.Label(form_frame, text="结束时间：").grid(row=3, column=0, sticky="w")
        self.end_entry = tk.Entry(form_frame, width=20)
        self.end_entry.grid(row=3, column=1, sticky="w")

        # 添加手动任务按钮
        # ???
        self.manual_btn = tk.Button(form_frame, text="添加手动任务")
        self.manual_btn.grid(row=4, column=1, pady=10, sticky="e")

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
        self.start_btn = tk.Button(timer_frame, text="开始任务")
        self.start_btn.pack(side=tk.LEFT, padx=10)
        self.stop_btn = tk.Button(timer_frame, text="停止任务", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

    def _build_task_list(self):
        """创建任务列表的界面组件"""
        self.list_frame = tk.Frame(self.window)
        self.list_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # 修改列的定义，这里区分一下Treeview的三个参数，pycharm注释给的不好：
        # show：tree/headings/both树状/表格/全部结构展示
        # selectmode：treeview中选择项的方式
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

    def refresh_task_list(self, tasks):
        """清除列表全部内容然后从数据库重新加载以达到刷新效果"""

        # 清空现有数据
        # get_children()返回所有子项，
        for item in self.task_list.get_children():
            self.task_list.delete(item)

        # 遍历任务列表，已完成任务算出时间，未完成任务给duration标注进行中
        for row in tasks:
            duration_seconds = row[5]
            if duration_seconds is not None:
                hours = duration_seconds // 3600
                minutes = (duration_seconds % 3600) // 60
                duration = f"{hours}小时{minutes}分钟"
            else:
                duration = "进行中"
            self.task_list.insert("", tk.END, values=(row[0], row[1], row[2], row[3], row[4], duration))

    def set_manual_task_handler(self, handler):
        """
            绑定手动任务按钮的点击事件处理器

            [MVC 架构说明]
            本方法属于视图层向控制器层暴露的接口，用于实现控制反转（IoC），
            确保视图不包含任何业务逻辑，符合职责分离原则。

            Args:
                handler: callable - 必须是一个可调用对象（函数/方法），
                        当用户点击"添加手动任务"按钮时触发调用。
                        典型用法是由控制器传递处理方法（如：controller.handle_manual_task）

            [设计意图]
            1. 解耦视图与业务逻辑，使同一视图可适配不同控制器
            2. 便于单元测试时注入模拟处理器（mock handler）
            3. 避免视图层直接操作模型或数据库

            [调用示例]
            # 在控制器层
            class TaskController:
                def __init__(self, view):
                    view.set_manual_task_handler(self.handle_manual_task_event)

                def handle_manual_task_event(self):
                    # 实际业务逻辑...

            [注意事项]
            - 必须在视图初始化完成后调用（即按钮控件已创建）
            - handler 应负责数据验证、模型操作和界面更新协调
            """
        self.manual_btn.config(command=handler)

    def set_auto_handlers(self, start_handler, stop_handler):
        self.start_btn.config(command=start_handler)
        self.stop_btn.config(command=stop_handler)

    def get_manual_task_data(self):
        """此方法会返回手动任务的四个信息"""
        return {
            'category': self.category_combo.get(),
            'title': self.title_entry.get(),
            'start_time': self.start_entry.get(),
            'end_time': self.end_entry.get()
        }

    def clear_manual_inputs(self):
        # 删除所有手动输入的数据,计划用于数据插入数据库之后清除手动的记录
        self.title_entry.delete(0, tk.END)
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)

    def set_auto_controls_state(self, start_state, stop_state):
        """重置自动计时按钮的状态，start_state:开始状态；stop_state:终止状态"""
        self.start_btn.config(state=start_state)
        self.stop_btn.config(state=stop_state)
        self.auto_category.config(state='readonly' if start_state == tk.NORMAL else tk.DISABLED)

    def run(self):
        # 核心！无限循环、持续监听、随时准备触发回调函数
        self.window.mainloop()


if __name__ == "__main__":
    view = MainView()
    view.run()
