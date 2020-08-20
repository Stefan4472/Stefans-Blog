import sqlite3
from flask import current_app, g  # TODO: REMOVE
import datetime
import typing


class Database:
    def __init__(
            self, 
            db_path: str,
    ):
        self.db = \
            sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.db.row_factory = sqlite3.Row
        self.cur = self.db.cursor()

    def run_script(
            self, 
            script_str: str,
    ):
        self.cur.executescript(script_str)

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()

    def add_post(
            self, 
            title: str, 
            byline: str, 
            slug: str, 
            post_date: datetime.date, 
            featured_url: str, 
            banner_url: str, 
            thumbnail_url: str,
    ):
        """Creates an entry for a new post with the given meta-data.

        Throws ValueError if a database constraint is violated (e.g., a post
        with the provided slug already exists.
        """
        command = \
            'insert into Posts(post_title, post_byline, post_slug, ' \
                'post_date, post_image_url, post_banner_url, '\
                'post_thumbnail_url) values (?, ?, ?, ?, ?, ?, ?)'
        values = \
            (title, byline, slug, post_date, featured_url, \
                banner_url, thumbnail_url)
        try:
            self.cur.execute(command, values)
        except sqlite3.IntegrityError as e:
            raise ValueError(str(e))
        
    def get_post_by_slug(
            self, 
            slug: str,
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """Looks up and returns the post data for the given slug. May be None."""
        # TODO: CREATE A `POST` DATACLASS
        command = 'select * from Posts where post_slug = ?'
        values = (slug,)
        return self.cur.execute(command, values).fetchone()

    def get_post_by_postid(
            self, 
            post_id: int,
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        """Looks up and returns the post data for the given post ID.
        May be None.
        """
        command = 'select * from Posts where post_id = ?'
        values = (post_id,)
        return self.cur.execute(command, values).fetchone()

    def get_recent_posts(
            self, 
            num_posts: int,
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        """Returns the `num_posts` most recent posts, sorted by `post_date`
        descending (most recent first)."""
        command = 'select * from Posts order by post_date desc limit ?'
        values = (num_posts,)
        return self.cur.execute(command, values).fetchall()

    def get_all_posts(self):
        """Return a list of all post data."""
        command = 'select * from Posts order by post_date desc'
        return self.cur.execute(command).fetchall()

    def has_tag(
            self, 
            tag_slug: str,
    ) -> bool:
        """Return whether the specified tag exists in the database."""
        command = 'select * from Tags where tag_slug = ?'
        values = (tag_slug,)
        return bool(self.cur.execute(command, values).fetchone())

    def add_tag(
            self, 
            name: str, 
            slug: str, 
            color: str,
    ):
        """Create a tag with the given values in the database.

        Throws ValueError if a tag with the given slug already exists.
        """
        command = \
            'insert into Tags(tag_title, tag_slug, tag_color) values (?, ?, ?)'
        values = (name, slug, color)
        try:
            self.cur.execute(command, values)
        except sqlite3.IntegrityError as e:
            raise ValueError(str(e))

    def get_tag_by_tagid(
            self, 
            tag_id: str,
    ) -> typing.Optional[typing.Dict]:
        """Lookup and return data for the tag with the provided id.

        Returns None if the tag could not be found.
        TODO: CREATE A `TAG` DATACLASS
        """
        command = 'select * from Tags where tag_id = ?'
        values = (tag_id,)
        return self.cur.execute(command, values).fetchone()

    def get_tag_by_tagslug(
            self, 
            tag_slug: str,
    ) -> typing.Optional[typing.Dict]:
        command = 'select * from Tags where tag_slug = ?'
        values = (tag_slug,)
        return self.cur.execute(command, values).fetchone()

    def add_tag_to_post(
            self, 
            tag_slug: str,
            post_slug: str,
    ):
        """Link the specified tag to the specified post."""
        command = 'insert into PostsToTags values (?, ?)'
        values = (post_slug, tag_slug)
        self.cur.execute(command, values)

    # note: debugging
    def get_all_tags(self) -> typing.List[typing.Dict]:
        return self.cur.execute('select * from Tags', ()).fetchall()
    def get_all_relations(self) -> typing.List[typing.Dict]:
        return self.cur.execute('select * from PostsToTags', ()).fetchall()

    def get_tags_by_post_slug(
            self, 
            post_slug: str,
    ) -> typing.List[typing.Dict]:
        """Get all tags associated with the specified post.
        
        See https://stackoverflow.com/questions/16549971/join-tables-in-sqlite-with-many-to-many
        for a good example of retrieving many-to-many relations
        """
        command = \
            'select t.tag_id, t.tag_title, t.tag_slug, t.tag_color ' \
                'from Tags t left join PostsToTags pt ' \
                'on pt.tag_slug = t.tag_slug where pt.post_slug = ?'
        values = (post_slug,)
        return self.cur.execute(command, values).fetchall()

    def get_posts_by_tag_slug(
            self, 
            tag_slug: str,
    ) -> typing.List[typing.Dict]:
        """Get all posts associated with the given tag."""
        command = \
            'select p.post_id, p.post_title, p.post_byline, '\
                'p.post_slug, p.post_date, p.post_image_url, '\
                'p.post_banner_url, p.post_thumbnail_url from Posts p left join '\
                'PostsToTags pt on p.post_slug = pt.post_slug ' \
                'where pt.tag_slug = ?'
        values = (tag_slug,)
        return self.cur.execute(command, values).fetchall()
        
# get database for the current request
# will be stored under 'db' in the current request object "g"
def get_db():
    if 'db' not in g:
        # print ('Retrieving database at {}'.format(current_app.config['DATABASE_PATH']))
        g.db = Database(current_app.config['DATABASE_PATH'])

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