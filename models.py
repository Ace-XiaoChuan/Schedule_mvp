import sqlite3
from datetime import datetime


class TaskModels:
    def __init__(self, db_path="schedule.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        """创建数据表（如果不存在的话）"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                is_auto INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def add_manual_task(self, title, category, start_time, end_time=None):
        """添加手动任务，本方法会往数据库tasks表里插入以下数据：
        (title, category, start_time, end_time, is_auto)"""

        try:
            # 验证时间格式，model层应该负责做数据验证
            datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            # 如果任务已完成：数据插入数据库
            if end_time:
                datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

            self.conn.execute(
                """INSERT INTO tasks 
                (title, category, start_time, end_time, is_auto) 
                VALUES (?, ?, ?, ?, ?)""",
                (title, category, start_time, end_time, 0)
            )
            self.conn.commit()
            return True
        except(ValueError, sqlite3.Error) as e:
            raise Exception(f"操作失败：{str(e)}")

    def add_auto_task(self, title, category, start_time, end_time):
        """添加自动计时类型任务"""
        try:
            # 先验证时间格式,格式化输入的st和et,再把4条数据插入tasks
            datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            self.conn.execute("""
                INSERT INTO tasks
                (title,category,start_time,end_time,is_auto)
                VALUES (?,?,?,?,?)
            """, (title, category, start_time, end_time, 1))
            self.conn.commit()
            return True
        except (ValueError, sqlite3.Error) as e:
            raise Exception(f"操作失败：{str(e)}")

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
