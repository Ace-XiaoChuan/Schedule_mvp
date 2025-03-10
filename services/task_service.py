"""模块文档级字符串
tasks_service
---
基础服务层，存放核心业务逻辑
功能概述：暂无
"""
from core.exceptions import ValidationError
from datetime import datetime
from core import config


class TaskService:
    def __init__(self, repository, classifier):
        self.repository = repository
        self.classifier = classifier

    def create_task(self, task_data: dict) -> int:
        """
        创建任务的统一逻辑,在main里被使用
        :param task_data:用户输入的字典，见main->handle_manual_task
        :return:
        """
        # 无标题验证：
        if not task_data.get("title"):
            raise ValidationError("任务标题不能为空")
        # 无开始时间验证
        if not task_data.get("start_time"):
            raise ValidationError("开始时间不能为空")
        # 如果是自动计时而且没有结束时间
        if task_data.get("is_auto") == 1 and not task_data.get("end_time"):
            raise ValidationError("自动任务必须设置结束时间！")
        # 时间顺序验证（大小不能倒置）
        start_time = datetime.strptime(task_data["start_time"], config.datetime_formation)
        if task_data.get("end_time"):
            end_time = datetime.strptime(task_data["end_time"], config.datetime_formation)
            if end_time < start_time:
                raise ValidationError("结束时间不能早于开始时间")
        return self.repository.add_task(task_data)
