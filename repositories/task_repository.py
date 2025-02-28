import sqlite3
from datetime import datetime


class TaskRepository:
    def __init__(self, conn):
        # 数据库交互接口；通过 conn.commit() 等方法，进行事务管理，实现原子化；外部传入，依赖注入
        self.conn = conn
        self._create_table()

    def _create_table(self):
        """
        创建数据表
        :return:
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
        通用的添加任务的方法
        :param task_data:传入一个字典，应为[title, category, start_time, end_time, is_auto]格式
        :return:最后一行的主键
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
            raise Exception(f"数据库操作失败：{str(e)}")
