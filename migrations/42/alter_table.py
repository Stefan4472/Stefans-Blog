import sqlite3

SQLITE_PATH = r'C:\Users\stefa\Documents\Stefans-Blog\instance\posts.db'


if __name__ == '__main__':
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    cur.execute("ALTER TABLE post ADD COLUMN title_color VARCHAR(8) DEFAULT '0xFFFFFF'")
    conn.commit()
