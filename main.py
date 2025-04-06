from controllers.task_controller import TaskController
from view import MainView
from fastapi import FastAPI, HTTPException  # 导入 FastAPI 框架，用于创建 Web API
import threading
from models import TaskModels
from pydantic import BaseModel  # pedantic数据验证和设置管理
from ai.ai_classifier import SimpleClassifier
import uvicorn  # uvicorn，用于启动 FastAPI 的 ASGI 服务器
# ASGI（Asynchronous Server Gateway Interface，异步服务器网关接口）是 Python 服务器和 Web 应用之间的一种通信协议，
# 它是 WSGI（Web Server Gateway Interface）的进化版本，专门用于支持异步 Web 框架，如 FastAPI 和 Django Channels。
from core.exceptions import ValidationError  # 复用原有异常

classifier = SimpleClassifier()


# 定义请求模型（复用原有数据格式）
class TaskRequest(BaseModel):
    title: str
    category: str
    start_time: str
    end_time: str | None = None  # end_time: (str | None) = None
    is_auto: bool = False


def run_desktop_app():
    """运行Tkinter桌面应用"""
    view = MainView()
    desktop_app = TaskController(view)
    try:
        desktop_app.run()
    finally:
        desktop_app.shutdown()


app = FastAPI()


@app.get("/tasks")  # 使用 @app.get("/tasks") 装饰一个函数时，FastAPI 会把该函数注册为处理 /tasks 路径的 GET 请求。
# 也就是说，当客户端发送 GET 请求到 /tasks 时，这个函数就会被调用。
def get_tasks():
    """测试接口：返回简单的任务数据
        定义一个 GET 接口 /tasks。
        当通过 HTTP GET 请求访问 /tasks 时，返回一个简单的任务数据（这里用中文描述任务）。
        """
    return {"tasks": ["学习Python", "健身30分钟"]}


@app.get("/classify")
def classify_title(title: str):
    category, confidence = classifier.predict(title)# 调用AI模型预测
    return {"category": category, "confidence": confidence}


@app.post("/tasks")
def create_task(task: TaskRequest):
    try:
        # 自动分类标题
        if task.title:
            predicted_category, confidence = classifier.predict(task.title)
            task.category = predicted_category  # 覆盖用户输入的分类
        # 将Pydantic模型转为字典，适配原有代码
        task_data = task.dict()
        task_data["is_auto"] = 1 if task_data["is_auto"] else 0  # 转换布尔值为整数

        # 直接调用原有仓储层（跳过Tkinter）
        db = TaskModels("tasks.db")
        task_id = db.repository.add_task(task_data)
        db.close()

        return {"id": task_id, "status": "created"}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="服务器内部错误")


def run_fastapi():
    """
        运行 FastAPI 应用的函数。
        使用 uvicorn 作为服务器，在指定的地址和端口上运行 FastAPI 应用。
        """
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # 当作为主程序运行时，启动多线程同时运行 FastAPI 服务和桌面应用。
    # 启动 FastAPI 服务的线程设置为守护线程（daemon），保证主线程结束时也会结束该线程
    threading.Thread(target=run_fastapi, daemon=True).start()
    # 运行桌面应用（例如：Tkinter 应用），此函数会阻塞主线程直到应用退出
    run_desktop_app()  # 启动原有的桌面应用
