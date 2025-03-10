import sqlite3
from datetime import datetime
from core.exceptions import DatabaseError


class TaskRepository:
    """
    # 仓储层-数据库操作的核心实现类
    ## 职责说明：
        - 管理任务数据的持久化操作
        - 封装具体数据库的视线细节
        - 保证实际操作的原子性
    ## 设计特点：
        - 依赖注入：通过构造函数接收数据库连接对象（conn）
        - 单一职责：每个方法只处理单一数据库操作
        - 异常隔离：捕获底层数据库异常并向上层抛出
    """

    def __init__(self, conn: sqlite3.Connection):
        """初始化仓储实例
            :param conn: 已建立的数据库连接对象（来自Model层）
        """
        self.conn = conn
        self._create_table()

    def _create_table(self):
        """
        表结构说明：
          - id          : 自增主键
          - title       : 任务标题（非空）
          - category    : 分类标签（工作/休闲/睡眠）
          - start_time  : 开始时间（ISO8601格式）
          - end_time    : 结束时间（允许为空）
          - is_auto     : 自动任务标记（0/1）
        """
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                is_auto INTEGER DEFAULT 0)
                """)
        self.conn.commit()

    def add_task(self, task_data: dict) -> int:
        """
        :param task_data: 包含任务数据的字典，必须包含以下键：
            - title       : 任务标题（str）
            - category    : 分类标签（str）
            - start_time  : 开始时间（str，格式：%Y-%m-%d %H:%M:%S）
            - end_time    : 结束时间（str，可选）
            - is_auto     : 是否自动任务（int，默认0）
        :return: 新插入记录的ID（lastrowid）
        :raises:
            ValueError - 当时间格式不合法时
            sqlite3.Error - 数据库操作失败时
        """
        try:
            # 先验证时间格式
            datetime.strptime(task_data["start_time"], "%Y-%m-%d %H:%M:%S")
            if task_data["end_time"]:
                datetime.strptime(task_data["end_time"], "%Y-%m-%d %H:%M:%S")
            # cursor：游标对象，承载SQL执行后的结果并提供一些附加信息（如那个lastrowid）
            # 1.cursor是执行结果的的封装
            # 2.获取附加信息：对于 INSERT 操作，游标对象的 lastrowid 属性可以返回最后一次插入记录时自动生成的主键值。这在需要知道新插入记录的 ID 时非常有用。
            # 具体定义过程都在sqlite3里完成了，使用者就关注对外暴露的这个接口的几个常用属性，比如lastrowid\rowcount\description还有几个方法即可
            cursor = self.conn.execute(
                """INSERT INTO tasks 
                (title, category, start_time, end_time, is_auto)
                VALUES (?, ?, ?, ?, ?)""",
                (
                    task_data["title"],
                    task_data["category"],
                    task_data["start_time"],
                    task_data["end_time"],
                    task_data.get("is_auto", 0)
                )
            )
            self.conn.commit()
            return cursor.lastrowid
        except (ValueError, sqlite3.Error) as e:
            raise DatabaseError(
                f"数据库操作失败：{str(e)}",
                #     未来可能的错题报告...
            )
