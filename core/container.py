from pathlib import Path
from repositories.task_repository import TaskRepository
from services.task_service import TaskService
from ai.ai_classifier import SimpleClassifier
from models import TaskModels


class Container:
    def __init__(self):
        # 初始化model和仓储层
        self.models = TaskModels()
        self.task_repository = TaskRepository(self.models.conn)

        # 延迟初始化分类器（避免重复训练）
        self._classifier = None

        # 不知道为什么，但是d指导要求我懒加载，那么就懒加载
        self.task_service = TaskService(
            repository=self.task_repository,
            classifier=self.classifier
        )

    @property
    def classifier(self):
        """惰性加载分类器"""
        """引入懒加载的意义是什么？"""
        if self._classifier is None:
            self._classifier = SimpleClassifier()

            try:
                # 检查是否已有训练好的模型
                if not Path(self._classifier.model_path).exists():
                    # print("🔄 未检测到训练模型，开始训练...")
                    self._classifier.train()
                else:
                    print("✅ 检测到已训练模型，跳过训练")
            except Exception as e:
                raise RuntimeError(f"分类器初始化失败：{str(e)}")
        return self._classifier
