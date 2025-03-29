"""模块文档级字符串
tasks_manager
---
服务层扩展，存放核心业务逻辑
功能概述：协调服务层和模型层，处理控制器委托的**业务逻辑**
"""
import logging
from core.exceptions import ValidationError, AIClassificationError

logger = logging.getLogger('schedule_mvp')


class TaskManager:
    """服务层的任务管理器组件，旨在协调处理手动任务相关的业务"""

    def __init__(self, task_service, model):
        self.task_service = task_service
        self.model = model
        logger.info("TaskManager初始化完成")

    def create_manual_task(self,task_data):
        """处理手动任务的创建流程"""

