from flaskr import db


class Image(db.Model):
    __tablename__ = 'images2'  # TODO: SET TO `images` ONCE READY. THEN DELETE THE ORIGINAL `POSTIMAGE` CLASS
    # TODO: MAKE THIS INTO A UUID. BUT THAT WILL REQUIRE POSTGRES
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String)
    # Original name at time of upload
    upload_name = db.Column(db.String)
    upload_date = db.Column(db.DateTime)
    # File extension
    extension = db.Column(db.String)
    # MD5 hash
    hash = db.Column(db.String, nullable=False)
    # Image dimensions (pixels)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    # TODO: MAKE ONE-TO-MANY
    # post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    # __unique_constraint__ = db.UniqueConstraint('id', 'filename')

    # def __repr__(self):
    #     return 'PostImage(filename="{}", hash="{}", post_id={})'.format(
    #         self.filename,
    #         self.hash,
    #         self.post_id,
    #     )
