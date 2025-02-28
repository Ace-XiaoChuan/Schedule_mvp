import sqlite3
from datetime import datetime
from repositories.task_repository import TaskRepository


class TaskModels:
    def __init__(self, db_path="schedule.db"):
        self.conn = sqlite3.connect(db_path)
        self.repository = TaskRepository(self.conn)

    def add_task(self, task_data: dict) -> int:
        """添加任务（无论手动/自动）"""
        return self.repository.add_task(task_data)

    def get_all_tasks(self):
        """获取所有已完成的任务,按开始的时间降序排列"""
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
