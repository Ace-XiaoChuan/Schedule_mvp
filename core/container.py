from pathlib import Path
from ai.ai_classifier import SimpleClassifier
from models import TaskModels
from .config import Appconfig


class Container:
    """
    表示层 → 控制器层 → 服务层 → 仓储层 → 模型层 → 数据层 → 核心层 | 基础设施层
        依赖注入容器（Dependency Injection Container）
        基础设施层
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

        """组合关系初始化核心基础设施层组件"""
        # 延迟初始化，在Python中构造方法中声明所有属性是一种良好实践
        # 初始化为空值暗示没有完成初始化。
        # 声明(Declaration)：创建变量名
        # 分配(Assignment)：给变量赋值
        # 初始化(Initialization)：首次给变量赋予有意义的值
        # 实例化(Instantiation)：创建类的实例对象
        # 所以这里只是声明并且分配，但是没有初始化和实例化，其实没什么意义

        self.config = Appconfig()
        self.models = TaskModels(str(self.config.DB_PATH))  # 数据库模型管理器
        self._task_repository = None
        self._classifier = None
        self._task_service = None


    @property
    def task_repository(self):
        # 使用构造器在这里的意义：
        if self._task_repository is None:
            # 在这里导入，避免循环依赖，也可以说是懒加载
            from repositories.task_repository import TaskRepository
            self._task_repository = TaskRepository(self.models.conn)
        return self._task_repository

    @property
    def task_service(self):
        if self._task_service is None:
            # 在这里导入，避免循环依赖
            from services.task_service import TaskService
            self._task_service = TaskService(
                # 高明的地方。外部代码直接使用container.task_Repository,不需要知道是属性还是方法。
                repository=self.task_repository,
                classifier=self.classifier
            )
        return self._task_service

    @property
    def classifier(self):
        """
        分类器属性的惰性加载实现
          1. 首次访问时检查模型文件是否存在
          2. 不存在则触发训练并保存模型
          3. 存在则直接加载已有模型
        """
        # 分类器不存在：延迟创建
        if self._classifier is None:
            # 确保单例。同时SimpleClassifier 的实例完全由 Container 管理，外部代码无法直接访问或控制这个实例。
            from ai.ai_classifier import SimpleClassifier
            self._classifier = SimpleClassifier(
                max_features=self.config.MAX_FEATURES,
                n_estimators=self.config.N_ESTIMATORS
            )  # 创建分类器实例，不是构造方法内，但是懒加载只是延迟了对象创建的时间点，
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
        # 分类器存在：直接返回
        return self._classifier
