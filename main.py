from datetime import datetime
import tkinter as tk
import tkinter.messagebox as messagebox
from models import TaskModels
from view import MainView
from ai.ai_classifier import SimpleClassifier


class TaskController:
    def __init__(self):
        # 初始化控制器：模型、视图
        # 初始化分类器：ai训练模型
        print("初始化控制器...")
        self.model = TaskModels()
        self.view = MainView()

        print("初始化分类器...")
        self.classifier = SimpleClassifier()

        try:
            self.classifier.train()  # 确保训练模型（或检查已有模型）
        except Exception as e:
            print(f"训练失败：{str(e)}")
            return

        print("绑定事件监听器...")

        # .bind()将一个事件与一个回调函数绑定。
        # "<KeyRelease>" 是事件类型，表示键盘按键松开时触发。
        self.view.title_entry.bind("<KeyRelease>", self.auto_classify)
        print("控制器初始化完成")

        # 绑定事件处理器1:设置手动任务处理器（依赖倒置原则）
        self.view.set_manual_task_handler(self.handle_manual_task)
        # 绑定事件处理器2：设置自动任务处理器
        self.view.set_auto_handlers(self.start_auto_task, self.stop_auto_task)

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
            self.model.add_task({
                "title": data["title"],
                "category": data["category"],
                "start_time": data["start_time"],
                "end_time": data["end_time"],
                "is_auto": 0
            })
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
        self.view.timer_status.config(text="计时中...", foreground="#2196F3")
        self.view.set_auto_controls_state(tk.DISABLED, tk.NORMAL)

    def stop_auto_task(self):
        """停止自动计时类型的任务"""
        # 如果当前没有自动计时任务：
        if not self.current_auto_task:
            return

        # 如果当前有自动计时任务：
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # 把任务加入列表
            self.model.add_task({
                "title": self.current_auto_task["title"],
                "category": self.current_auto_task["category"],
                "start_time": self.current_auto_task["start_time"],
                "end_time": end_time,  # 使用新生成的结束时间
                "is_auto": 1  # 明确标记为自动任务
            })
            self.current_auto_task = None
            self.view.set_auto_controls_state(tk.NORMAL, tk.DISABLED)
            self.refresh_task_list()

        except Exception as e:
            messagebox.showerror("错误", str(e))
        self.view.timer_status.config(text="计时已停止", foreground="#9E9E9E")

    def refresh_task_list(self):
        """刷新任务列表"""
        tasks = self.model.get_all_tasks()
        self.view.refresh_task_list(tasks)

    def auto_classify(self, current_text):
        """此方法用于自动将输入的内容分类，详情见ai/ai_classifier"""
        """处理键盘输入事件"""
        text = self.view.title_entry.get()
        try:
            if len(text) < 3:
                self.view.show_confidence("", 0)
                return

            pred_category, confidence = self.classifier.predict(text)
            self.view.show_confidence(pred_category, confidence)

        except Exception as e:
            print(f"自动分类异常：{str(e)}")
            self.view.show_confidence("", 0)

    def run(self):
        """应用，启动"""
        self.view.run()


if __name__ == "__main__":
    app = TaskController()
    app.run()
