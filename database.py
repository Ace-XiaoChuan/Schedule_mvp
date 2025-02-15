import sqlite3


class Database:
    def __init__(self, db_name="schedule.db"):
        self.conn = sqlite3.connect(db_name)
        self._create_table()

    def _create_table(self):
        # 建一个表，表名叫tasks，有就不管，没有就建
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_time TEXT)
            """)
        # 不commit，可能只保存在内存里，容易回滚
        self.conn.commit()


if __name__ == "__main__":
    db = Database()
    print("数据库已完成初始化")
