import sys
import sqlite3


if __name__ == '__main__':
    """
    Run migration for Issue #42.

    This program will add a column called "title_color" to the "posts"
    table in the database. 

    FILEPATH: path to the SQLITE database file
    """
    if len(sys.argv) != 2:
        print('Usage: python run_migration.py [FILEPATH]')
        sys.exit(1)
    conn = sqlite3.connect(sys.argv[1])
    cur = conn.cursor()
    cur.execute("ALTER TABLE post ADD COLUMN title_color VARCHAR(7) DEFAULT '#FFFFFF'")
    conn.commit()
