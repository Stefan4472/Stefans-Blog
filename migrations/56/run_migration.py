import sys
import sqlite3
import pathlib
from stefansearch.engine.search_engine import SearchEngine

if __name__ == '__main__':
    """
    Run migration for Issue #56.

    This program will re-index all posts. Run it on the deployed server.

    It accesses the database and search index without using the Flask context
    at all--a pretty brutal workaround if you ask me. I'll need to look into
    how to access the Flask context from an external script some other time.
    But for now, this will do.

    DB_PATH: path to the SQLITE database file
    INDEX_PATH: path to the search engine index file
    STATIC_PATH: path to the STATIC folder 
    """
    if len(sys.argv) != 4:
        print('Usage: python run_migration.py [DB_PATH] [INDEX_PATH] [STATIC_PATH]')
        sys.exit(1)

    db_path = pathlib.Path(sys.argv[1])
    index_path = pathlib.Path(sys.argv[2])
    static_path = pathlib.Path(sys.argv[3])

    search_engine = SearchEngine(index_path)
    search_engine.clear_all_data()
    conn = sqlite3.connect(str(db_path.resolve()))
    cur = conn.cursor()
    cur.execute("SELECT slug FROM post")
    for record in cur.fetchall():
        slug = record[0]
        md_path = static_path / slug / 'post.md'
        search_engine.index_file(md_path, slug, encoding='utf-8', allow_overwrite=True)
    conn.close()
    search_engine.commit()
