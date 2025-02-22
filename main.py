from datetime import datetime
import tkinter as tk
import tkinter.messagebox as messagebox
from models import TaskModels
from view import MainView


class TaskController:
    def __init__(self):
        # 初始化模型与视图
        self.model = TaskModels()
        self.view = MainView()

        # 绑定事件处理器1:设置手动任务处理器
        self.view.set_manual_task_handler(self.handle_manual_task)
        # 绑定事件处理器2：设置自动任务处理器
        self.view.set_auto_handlers(self.start_auto_task,self.stop_auto_task)

        # 初始化任务列表
        self.refresh_task_list()

    def handle_manual_task(self):
        """处理手动任务的添加"""
        data = self.view.get_manual_task_data()
        if not data["title"] or not data["start_time"]:
            messagebox.showerror("错误！", "任务标题和开始的时间不能为空")
            return
        # 如果非空：
        try:
            self.model.add_manual_task(
                data["title"],
                data["category"],
                data["start_time"],
                data["end_time"]
            )
            self.view.clear_manual_inputs()
            self.refresh_task_list()
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def start_auto_task(self):
        """启动自动计时类型的任务"""
        self.current_auto_task = {
            "title": "自动记录任务",
            "category": self.view.auto_category.get(),
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.view.set_auto_controls_state(tk.DISABLED, tk.NORMAL)

    def stop_auto_task(self):
        """停止自动计时类型的任务"""
        # 如果当前没有自动计时任务：
        if not self.current_auto_task:
            return

        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # 把任务加入列表
            self.model.add_auto_task(
                self.current_auto_task["title"],
                self.current_auto_task["category"],
                self.current_auto_task["start_time"],
                end_time
            )
            self.current_auto_task = None
            self.view.set_auto_controls_state(tk.NORMAL, tk.DISABLED)
            self.refresh_task_list()

        except Exception as e:
            messagebox.showerror("错误", str(e))

    def refresh_task_list(self):
        """刷新任务列表"""
        tasks = self.model.get_all_tasks()
        self.view.refresh_task_list(tasks)

    def run(self):
        """应用，启动"""
        self.view.run()

if __name__ == "__main__":
    app = TaskController()
    app.run()
