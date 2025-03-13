import sqlite3
from datetime import datetime
from repositories.task_repository import TaskRepository


# 仅定义数据结构和数据库连接，不直接操作数据。

class TaskModels:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.repository = TaskRepository(self.conn)

    def add_task(self, task_data: dict) -> int:
        """添加任务（无论手动/自动）"""
        return self.repository.add_task(task_data)

    def get_all_tasks(self):
        """
        获取所有已完成的任务,按开始的时间降序排列
        :return:返回一个列表，列表中的每个元素是一个元组，代表一行数据‌
        """
        cursor = self.conn.execute("""
        SELECT id,title,category,start_time,end_time,
        (strftime('%s',end_time)-strftime('%s',start_time))
        FROM tasks WHERE end_time IS NOT NULL ORDER BY start_time DESC
        """)
        return cursor.fetchall()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
