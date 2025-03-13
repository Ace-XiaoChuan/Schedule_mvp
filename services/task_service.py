"""模块文档级字符串
tasks_service
---
服务层，存放核心业务逻辑
功能概述：调用仓储层接口，处理业务逻辑，避免直接操作数据库。
"""
from core.exceptions import ValidationError
from datetime import datetime
from core import config
from pathlib import Path
import csv


class TaskService:
    def __init__(self, repository, classifier):
        # 这里的仓储层在服务层中被依赖，这很号，符合规范
        self.repository = repository
        self.classifier = classifier
        self.train_file = Path("ai/tasks.csv")

    def _init_training_file(self):
        """此方法用于确保训练文件存在，
        - 存在：跳过
        - 不存在：创建
        """
        if not self.train_file.exists():
            with open(self.train_file, "w", encoding='utf-8', newline='', ) as f:
                writer = csv.writer(f)
                writer.writerow(['task_name', 'category'])

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
        with open(self.train_file, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                task_data['title'].strip(),
                task_data['category'].strip()
            ])
        return self.repository.add_task(task_data)
