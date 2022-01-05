import hashlib
import shutil
import marshmallow
import typing
import sqlalchemy
import datetime as dt
from flask import request, Response, current_app, Blueprint, jsonify
from flask_login import login_required
import flaskr.api.constants as constants
import flaskr.api.util as util
from flaskr.database import db
from flaskr.models.post import Post
from flaskr.models.image import Image
from flaskr.models.tag import Tag
from flaskr.contracts.create_post import CreatePostContract
from renderer import markdown as md2
# TODO: Should have a set of Tag endpoints too
# TODO: SETUP TESTING FRAMEWORK


# Blueprint under which all views will be assigned
BLUEPRINT = Blueprint('posts', __name__, url_prefix='/api/v1/posts')


@BLUEPRINT.route('/', methods=['GET'])
@login_required
def get_posts():
    """
    Get a JSON "manifest" of posts.

    Query parameters:
    (bool) `featured`: return only posts where is_featured = ?
    (bool) `published`: return only posts where is_published = ?
    """
    # Create query dynamically based on the parameters passed in the request
    query = Post.query
    if constants.KEY_FEATURE in request.args:
        as_bool = (request.args[constants.KEY_FEATURE].lower() == 'true')
        query = query.filter(Post.is_featured == as_bool)
    if constants.KEY_PUBLISH in request.args:
        as_bool = (request.args[constants.KEY_PUBLISH].lower() == 'true')
        query = query.filter(Post.is_published == as_bool)

    manifest = {}
    for post in query.all():
        manifest[post.slug] = post.to_dict()
    return jsonify({'posts': manifest})


# Commit #1: Change create_post and the site_manager logic. Get it working
# Commit #2: Add PUT (edit) and PATCH methods. Change `Post` model to require all args on creation
# Commit #3: cleanup (especially sitemanager)
@BLUEPRINT.route('', methods=['POST'])
@login_required
def create_post():
    """
    Creates a post with the specified configuration and an empty Markdown
    text.

    I wanted to make this endpoing also require a Markdown file upload,
    but accepting JSON data *and* an uploaded file is tricky. That's
    why I split the Markdown out into its own sub-resource.

    Returns 400 if a post with the given slug already exists.
    """
    try:
        contract = CreatePostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    if Post.query.filter_by(slug=contract.slug).first():
        msg = 'A post with the given slug already exists'
        return Response(response=msg, status=400)

    try:
        post = Post(
            contract.slug,
            contract.title,
            get_image(contract.image),
            get_image(contract.banner),
            get_image(contract.thumbnail),
            byline=contract.byline,
            publish_date=dt.datetime(contract.date.year, contract.date.month, contract.date.day),
            is_featured=contract.feature,
            is_published=contract.publish,
            title_color=contract.title_color,
            tags=get_or_create_tags(contract.tags),
        )
        db.session.add(post)
        db.session.commit()
        return Response(status=200)
    except ValueError as e:
        return Response(status=400, response=str(e))
    except sqlalchemy.exc.SQLAlchemyError as e:
        # TODO: log error
        return Response(status=500, response='Internal database error')


@BLUEPRINT.route('/<string:slug>', methods=['DELETE'])
@login_required
def delete_post(slug: str):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)
    # Delete files, then delete record from DB
    shutil.rmtree(post.get_directory())
    Post.query.filter_by(slug=slug).delete()
    db.session.commit()
    return Response(status=200)


# TODO: EXPORT THIS FUNCTIONALITY INTO SOME KIND OF CONTROLLER CLASS
@BLUEPRINT.route('/<string:slug>/config', methods=['POST'])
@login_required
def set_config(slug: str):
    try:
        contract = CreatePostContract.from_json(request.get_json())
    except marshmallow.exceptions.ValidationError as e:
        return Response(status=400, response='Invalid parameters: {}'.format(e))

    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)

    # TODO: implement and use Post `setter()` methods
    if contract.title:
        post.title = contract.title
    if contract.byline:
        post.byline = contract.byline
    if contract.date:
        post.date = contract.date
    if contract.image:
        filename = contract.image
        found_image = Image.query.filter_by(filename=filename).first()
        if not found_image:
            msg = f'Specified image "{filename}" not found on server'
            return Response(response=msg, status=400)
        elif found_image.width != 1000 or found_image.height != 540:
            msg = f'Specified image "{filename}" has the wrong dimensions'
            return Response(response=msg, status=400)
        else:
            post.featured_filename = filename
            if found_image not in post.images:
                post.images.append(found_image)
    if contract.thumbnail:
        filename = contract.thumbnail
        found_image = Image.query.filter_by(filename=filename).first()
        if not found_image:
            msg = f'Specified image "{filename}" not found on server'
            return Response(response=msg, status=400)
        elif found_image.width != 400 or found_image.height != 400:
            msg = f'Specified image "{filename}" has the wrong dimensions'
            return Response(response=msg, status=400)
        else:
            post.thumbnail_filename = filename
            if found_image not in post.images:
                post.images.append(found_image)
    if contract.banner:
        filename = contract.banner
        found_image = Image.query.filter_by(filename=filename).first()
        if not found_image:
            msg = f'Specified image "{filename}" not found on server'
            return Response(response=msg, status=400)
        elif found_image.width != 1000 or found_image.height != 175:
            msg = f'Specified image "{filename}" has the wrong dimensions'
            return Response(response=msg, status=400)
        else:
            post.banner_filename = filename
            if found_image not in post.images:
                post.images.append(found_image)
    if contract.tags:
        # Add tags
        for tag_name in contract.tags:
            tag_slug = util.generate_slug(tag_name)
            # Lookup tag in the database
            tag = Tag.query.filter_by(slug=tag_slug).first()
            # Create tag if doesn't exist already
            if not tag:
                tag = Tag(
                    slug=tag_slug,
                    name=tag_name,
                    color=util.generate_random_color(),
                )
                db.session.add(tag)
            # Register the post under this tag
            tag.posts.append(post)
    if contract.publish:
        post.is_published = contract.publish
    if contract.feature:
        post.is_featured = contract.feature
    if contract.title_color:
        post.title_color = contract.title_color
    db.session.commit()
    return Response(status=200)


@BLUEPRINT.route('/<string:slug>/body', methods=['POST'])
@login_required
def upload_markdown(slug: str):
    """Upload the Markdown body of the post."""
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)

    try:
        raw_markdown, _ = util.get_uploaded_file(request)
    except ValueError as e:
        return Response(status=400, response=str(e))

    try:
        markdown = raw_markdown.decode('utf-8', errors='strict')
    except UnicodeError as e:
        msg = f'Error reading Markdown in UTF-8: {e}'
        return Response(status=400, response=msg)

    # Look up referenced images and ensure they exist on server.
    # Also update `post.images`.
    # TODO: honestly, this image stuff needs some real testing
    # TODO: how to track featured, banner, and thumbnail as images belonging to the post?
    post.images = []
    if post.featured_filename:
        post.images.append(Image.query.filter_by(filename=post.featured_filename).first())
    if post.banner_filename:
        post.images.append(Image.query.filter_by(filename=post.banner_filename).first())
    if post.thumbnail_filename:
        post.images.append(Image.query.filter_by(filename=post.thumbnail_filename).first())
    for image_name in md2.find_images(markdown):
        found_image = Image.query.filter_by(filename=image_name).first()
        if found_image:
            post.images.append(found_image)
        else:
            message = f'Image file not found on server: {image_name}'
            return Response(status=400, response=message)

    # Render HTML to check for errors
    try:
        md2.render_string(markdown)
    except Exception as e:
        return Response(status=400, response=f'Error processing Markdown: {e}')

    # Write out Markdown
    with open(post.get_markdown_path(), 'w+', encoding='utf-8') as out:
        out.write(markdown)

    # Update hash
    post.hash = hashlib.md5(raw_markdown).hexdigest()
    db.session.commit()

    # Add Markdown file to the search engine index
    # TODO: PROVIDE AN `INDEX_STRING()` METHOD
    current_app.search_engine.index_file(post.get_markdown_path(), slug)
    current_app.search_engine.commit()
    return Response(status=200)


def get_or_create_tags(tags: typing.List[str]) -> typing.List[Tag]:
    if tags:
        tag_objects: typing.List[Tag] = []
        for tag_name in tags:
            tag_slug = util.generate_slug(tag_name)
            tag_obj = Tag.query.filter_by(slug=tag_slug).first()
            # Create tag if doesn't exist already
            if not tag_obj:
                tag_obj = Tag(
                    slug=tag_slug,
                    name=tag_name,
                    color=util.generate_random_color(),
                )
                db.session.add(tag_obj)
            tag_objects.append(tag_obj)
        return tag_objects


def get_image(filename: str) -> Image:
    image = Image.query.filter_by(filename=filename).first()
    if not image:
        raise ValueError(f'Specified image "{filename}" not found on server')
    return image
