from datetime import datetime
import tkinter as tk
import tkinter.messagebox as messagebox
from models import TaskModels
from view import MainView
from ai import SimpleClassifier
from services import TaskService
from core import ValidationError, AIClassificationError, Container
from logging.handlers import RotatingFileHandler


class TaskController:
    def __init__(self):
        print("初始化控制器...")
        # 组合关系
        self.container = Container()
        self.view = MainView()
        self.model = self.container.models

        print("初始化分类器...")
        self.classifier = SimpleClassifier()

        # 通过容器获取服务层的实例
        self.task_service = self.container.task_service

        try:
            self.classifier.train()  # 确保训练模型（或检查已有模型）
        except Exception as e:
            print(f"训练失败：{str(e)}")
            return

        print("绑定事件监听器...")

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
        # 判断逻辑放到服务层了,同时引入分层错误验证功能
        try:
            task_data = {
                "title": data["title"],
                "category": data["category"],
                "start_time": data["start_time"],
                "end_time": data["end_time"],
                "is_auto": 0
            }
            self.task_service.create_task(task_data)  # 调用服务层
            self.view.clear_manual_inputs()
            self.refresh_task_list()

        except ValidationError as v:
            # 处理输入验证类型错误
            self.view.show_error(f"输入错误：{str(v)}", error_type="validation")

        except AIClassificationError as e:
            # 处理AI分类错误（业务逻辑问题）
            self.view.show_error(f"分类失败: {str(e)}", error_type="ai")

        except Exception as e:
            # 处理其他未知错误（系统级问题）
            self.view.show_error(f"系统错误: {str(e)}", error_type="system")

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
            self.task_service.create_task({
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

    def shutdown(self):
        # 关于为什么要显示的关闭数据库的连接，数据库的连接有点像句柄，会占用连接池
        self.model.close()

    def run(self):
        """应用，启动"""
        self.view.run()


if __name__ == "__main__":
    # 入口点检查，表示当此文件被直接运行而非作为模块导入其他文件时。
    app = TaskController()
    try:
        app.run()
    finally:
        # 无论正常还是崩溃都会shutdown
        app.shutdown()
