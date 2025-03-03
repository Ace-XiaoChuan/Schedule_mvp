# 统一的错误处理方式

class DomainError(Exception):
    """领域层基础异常"""
    pass


class ValidationError(DomainError):
    """数据验证失败异常"""
    pass


class AIClassificationError(DomainError):
    """AI分类异常"""
    pass


class DatabaseError(Exception):
    """数据库错误"""
    pass

# 关于这么做的目的：精确错误分类，每种异常类对应一种错误类型
