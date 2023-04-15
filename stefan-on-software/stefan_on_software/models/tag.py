import flask
from stefan_on_software import db
from stefan_on_software.contracts.data_schemas import TagContract


class Tag(db.Model):
    __tablename__ = "tag"
    slug = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    # Note: checking for valid hex colors is left to the application
    color = db.Column(db.String, nullable=False)

    def make_url(self, external: bool) -> str:
        return flask.url_for("blog.tag_view", slug=self.slug, _external=external)

    @property
    def relative_url(self) -> str:
        return self.make_url(False)

    @property
    def absolute_url(self) -> str:
        return self.make_url(True)

    def __repr__(self):
        return "Tag(slug={}, color={})".format(self.slug, self.color)

    def make_contract(self) -> TagContract:
        return TagContract(
            slug=self.slug,
            name=self.name,
            description=self.description,
            color=self.color,
        )
