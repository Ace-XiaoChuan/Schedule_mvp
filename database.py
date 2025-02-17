import sqlite3


class Database:
    def __init__(self, db_name="schedule.db"):
        self.conn = sqlite3.connect(db_name)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL CHECK(category IN ('工作','休闲','睡眠'))，
                start_time TEXT NOT NULL,
                end_time TEXT,
                is_auto BOOLEAN NOT NULL -- 0:手动记录，1:自动记录
                )
            """)
        # 不commit，可能只保存在内存里，容易回滚
        self.conn.commit()

    def insert_task(self, title, due_time):
        """插入新任务"""
        self.conn.execute(
            "INSERT INTO tasks (title, due_time) VALUES (?, ?)",
            (title, due_time)
        )
        self.conn.commit()

if __name__ == "__main__":
    db = Database()
    print("数据库已完成初始化")
