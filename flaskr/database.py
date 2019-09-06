import sqlite3
from flask import current_app, g

class Database:
    def __init__(self, db_path):
        self.db = \
            sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.row_factory = sqlite3.Row
        self.cur = self.db.cursor()

    def run_script(self, script_str):
        self.cur.executescript(script_str)

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()

    # attempts to create an entry for a new post with the
    # given data.
    # will throw ValueError if unsuccessful
    def add_post(self, title, byline, slug, post_date, post_image_name):
        query = 'insert into Posts values (NULL, ?, ?, ?, ?, ?)'
        values = (title, byline, slug, post_date, post_image_name)
        self.cur.execute(query, values)

    # returns post data for the given slug
    def get_post_by_slug(self, slug):
        query = 'select * from Posts where post_slug = ?'
        values = (slug,)
        return self.cur.execute(query, values).fetchone()

    def get_post_by_postid(self, post_id):
        query = 'select * from Posts where post_id = ?'
        values = (post_id,)
        return self.cur.execute(query, values).fetchone()

    # returns the [num_posts] most recent posts, sorted by post_date
    def get_recent_posts(self, num_posts):
        query = 'select * from Posts order by post_date desc limit {}'.format(num_posts)
        values = ()
        return self.cur.execute(query, values).fetchall()

    def get_all_posts(self):
        query = 'select * from Posts order by post_date desc'
        values = ()
        return self.cur.execute(query, values).fetchall()

    def has_tag(self, tag_slug):
        query = 'select * from Tags where tag_slug = ?'
        values = (tag_slug,)
        return self.cur.execute(query, values).fetchone() is not None

    def add_tag(self, name, slug, color=''):
        color = color if color else '#FF0000'  # TODO: RANDOM COLOR GENERATION FROM PALETTE
        query = 'insert into Tags values (NULL, ?, ?, ?)'
        values = (name, slug, color)
        self.cur.execute(query, values)

    def get_tag_by_tagid(self, tag_id):
        query = 'select * from Tags where tag_id = ?'
        values = (tag_id,)
        return self.cur.execute(query, values).fetchone()

    def get_tag_by_tagslug(self, tag_slug):
        query = 'select * from Tags where tag_slug = ?'
        values = (tag_slug,)
        return self.cur.execute(query, values).fetchone()

    def add_tag_to_post(self, tag_slug, post_slug):
        query = 'insert into PostsToTags values (?, ?)'
        values = (post_slug, tag_slug)
        self.cur.execute(query, values)

    # note: debugging
    def get_all_tags(self):
        return self.cur.execute('select * from Tags', ()).fetchall()
    def get_all_relations(self):
        return self.cur.execute('select * from PostsToTags', ()).fetchall()

    # see https://stackoverflow.com/questions/16549971/join-tables-in-sqlite-with-many-to-many
    # for a good example of retrieving many-to-many relations
    def get_tags_by_post_slug(self, post_slug):
        query = 'select t.tag_id, t.tag_title, t.tag_slug, t.tag_color ' \
                'from Tags t left join PostsToTags pt ' \
                'on pt.tag_slug = t.tag_slug where pt.post_slug = ?'
        values = (post_slug,)
        return self.cur.execute(query, values).fetchall()

    def get_posts_by_tag_slug(self, tag_slug):
        query = 'select p.post_id, p.post_title, p.post_byline, '\
                'p.post_slug, p.post_date from Posts p left join '\
                'PostsToTags pt on p.post_slug = pt.post_slug ' \
                'where pt.tag_slug = ?'
        values = (tag_slug,)
        return self.cur.execute(query, values).fetchall()
        
# get database for the current request
# will be stored under 'db' in the current request object "g"
def get_db():
    if 'db' not in g:
        print ('Retrieving database at {}'.format(current_app.config['DATABASE']))
        g.db = Database(current_app.config['DATABASE'])

    return g.db

# close database connection for the current request
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# initialize the database to the schema file, clearing all data  TODO: MOVE THIS TO __INIT__.PY?
def init_db():
    print ('Initializing database')
    db = get_db()
    with current_app.open_resource('posts_schema.sql') as f:
        db.run_script(f.read().decode('utf8'))