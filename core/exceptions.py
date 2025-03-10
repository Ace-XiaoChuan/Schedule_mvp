# 统一的错误处理方式

class DomainError(Exception):
    """领域层异常基类"""

    def __init__(self, msg: str, original_exc: Exception = None):
        super().__init__(msg)  # python内置的Exception是Cpython！不求甚解了。
        self.original_exc = original_exc  # 存储原始异常，可能能用得上
        self.context = {}  # 字典


class ValidationError(DomainError):
    """数据验证失败异常"""
    pass


class AIClassificationError(DomainError):
    """AI分类异常"""
    pass


class DatabaseError(Exception):
    """数据库错误"""
    pass


class TrainingError(DomainError):
    """模型训练异常"""

    def add_context(self, sample_count: int, feature_dim: int):
        self.context.update({  # context是父类继承来的
            'sample_count': sample_count,  # ？
            'feature_dim': feature_dim  # ？
        })

# 关于这么做的目的：精确错误分类，每种异常类对应一种错误类型
