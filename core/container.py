from repositories.task_repository import TaskRepository
from services.task_service import TaskService
from ai.ai_classifier import SimpleClassifier
from models import TaskModels


class Container:
    def __init__(self):
        # 初始化数据库连接
        self.models = TaskModels()

        # 初始化仓储层
        self.task_repository = TaskRepository(self.models.conn)

        # 初始化AI分类器
        self.classifier = SimpleClassifier()
        self.classifier.train()  # 确保训练完成

        # 初始化服务层
        self.task_service = TaskService(
            repository=self.task_repository,
            classifier=self.classifier
        )
