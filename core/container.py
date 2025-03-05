from pathlib import Path
from repositories.task_repository import TaskRepository
from services.task_service import TaskService
from ai.ai_classifier import SimpleClassifier
from models import TaskModels


class Container:
    """
        依赖注入容器（Dependency Injection Container）

        职责：
          1. 集中管理应用程序的核心组件
          2. 控制组件的生命周期和初始化顺序
          3. 实现依赖解耦，提升代码可测试性和可维护性

        设计特点：
          - 延迟初始化（Lazy Initialization）：按需创建资源密集型对象
          - 单一职责：每个组件仅通过容器获取依赖
          - 异常隔离：组件初始化错误统一处理
        """

    def __init__(self):
        """初始化核心基础设施层组件"""
        # 初始化数据访问层，这个在类的构造方法内创建无疑是组合关系
        self.models = TaskModels()  # 数据库模型管理器
        self.task_repository = TaskRepository(self.models.conn)  # 数据仓储实现

        # 延迟初始化分类器（设计关键点）
        self._classifier = None  # 实际分类器实例的占位符

        # 初始化服务层（依赖注入经典案例）
        # 注意：此处注入的是 classifier 的 property，实际使用时才会初始化
        self.task_service = TaskService(
            repository=self.task_repository,  # 注入数据仓储
            classifier=self.classifier  # 注入属性而非实例
        )

    @property
    def classifier(self):
        """
        分类器属性的惰性加载实现

        设计意义：
          1. 资源优化：避免应用启动时立即加载大模型
          2. 容错处理：将模型训练/加载的潜在错误延迟到实际使用时
          3. 状态管理：确保全局只有一个分类器实例（单例模式）

        初始化逻辑：
          1. 首次访问时检查模型文件是否存在
          2. 不存在则触发训练并保存模型
          3. 存在则直接加载已有模型
        """
        if self._classifier is None:
            # 确保单例。同时SimpleClassifier 的实例完全由 Container 管理，外部代码无法直接访问或控制这个实例。
            # 当 Container 实例被销毁时，SimpleClassifier 实例也会随之被垃圾回收，这进一步证明了生命周期的控制关系。
            self._classifier = SimpleClassifier()  # 创建分类器实例，不是构造方法内，但是懒加载只是延迟了对象创建的时间点，
            # 但不改变两个类之间的基本关系。当 classifier 属性第一次被访问时，SimpleClassifier 实例被创建并存储在 self._classifier 中，
            # 之后 Container 会一直持有这个引用。

            try:
                model_file = Path(self._classifier.model_path)
                if not model_file.exists():
                    # 模型不存在时的训练流程
                    self._classifier.train()  # 触发训练
                else:
                    # 模型已存在时的处理
                    print("✅ 检测到已训练模型，跳过训练")
            except Exception as e:
                # 统一异常转换（核心错误处理策略）
                raise RuntimeError(f"分类器初始化失败：{str(e)}") from e

        return self._classifier
