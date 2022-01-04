import hashlib
import datetime
import flask
import shutil
from flask import request, Response, current_app
from flask_login import login_required
from flaskr.database import db
from flaskr.models.post import Post, COLOR_REGEX
from flaskr.models.image import Image
from flaskr.models.tag import Tag
from flaskr import util
from renderer import markdown as md2
# TODO: Should have a set of Tag endpoints too
# TODO: SETUP TESTING FRAMEWORK


# Blueprint under which all views will be assigned
BLUEPRINT = flask.Blueprint('posts', __name__, url_prefix='/api/v1/posts')


@BLUEPRINT.route('/', methods=['GET'])
@login_required
def get_posts():
    """
    Get posts.

    Query parameters:
    (bool) `featured`: return only posts where is_featured = ?
    (bool) `published`: return only posts where is_published = ?
    """
    # Create query dynamically
    query = Post.query
    if 'featured' in request.args:
        # Convert string value to boolean value
        as_bool = (request.args['featured'].lower() == 'true')
        query = query.filter(Post.is_featured == as_bool)
    if 'published' in request.args:
        as_bool = (request.args['published'].lower() == 'true')
        query = query.filter(Post.is_published == as_bool)

    # Build JSON response
    manifest = {}
    for post in query.all():
        manifest[post.slug] = {
            util.KEY_SLUG: post.slug,
            util.KEY_TITLE: post.title,
            util.KEY_BYLINE: post.byline,
            util.KEY_DATE: post.date.strftime(util.DATE_FORMAT),
            util.KEY_IMAGE: post.featured_filename,
            util.KEY_BANNER: post.banner_filename,
            util.KEY_THUMBNAIL: post.thumbnail_filename,
            util.KEY_HASH: post.hash,
            util.KEY_TAGS: [tag.slug for tag in post.tags],
            util.KEY_IMAGES: {
                image.filename: {'hash': image.hash} for image in post.images
            },
            util.KEY_FEATURED: post.is_featured,
            util.KEY_PUBLISHED: post.is_published,
        }
    return flask.jsonify({'posts': manifest})


@BLUEPRINT.route('/<string:slug>', methods=['POST'])
@login_required
def create_post(slug: str):
    """
    Creates an empty post with the specified slug.

    Returns 400 if a post with the given slug already exists.
    """
    post = Post.query.filter_by(slug=slug).first()
    if post:
        msg = 'A post with the given slug already exists'
        return Response(response=msg, status=400)
    post = Post(slug=slug)
    post.get_directory().mkdir(exist_ok=True)
    db.session.add(post)
    db.session.commit()
    return Response(status=200)


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
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)
    config = request.get_json()
    # TODO: use string constants
    # TODO: implement and use Post `setter()` methods
    if 'title' in config:
        post.title = config['title']
    if 'byline' in config:
        post.byline = config['byline']
    if 'date' in config:
        post.date = datetime.datetime.strptime(config['date'], "%m/%d/%y").date()
    if 'image' in config:
        filename = config['image']
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
    if 'thumbnail' in config:
        filename = config['thumbnail']
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
    if 'banner' in config:
        filename = config['banner']
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
    if 'tags' in config:
        # Add tags
        for tag_name in config['tags']:
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
    if 'publish' in config:
        post.is_published = config['publish']
    if 'featured' in config:
        post.is_featured = config['featured']
    if 'title_color' in config:
        if not COLOR_REGEX.match(config['title_color']):
            msg = '"title_color" is not a valid hex color string ("#------")'
            return Response(status=400, response=msg)
        post.title_color = config['title_color']
    db.session.commit()
    return Response(status=200)


@BLUEPRINT.route('/<string:slug>/body', methods=['POST'])
@login_required
def upload_markdown(slug: str):
    """Upload the Markdown body of the post."""
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)

    if len(request.files) == 0:
        return Response(status=400, response='No file uploaded')
    elif len(request.files) > 1:
        return Response(status=400, response='More than one file uploaded')

    # Read uploaded file
    file = list(request.files.values())[0]
    raw_markdown = file.read()
    file.close()

    # Decode to utf-8
    try:
        markdown = raw_markdown.decode('utf-8', errors='strict')
    except UnicodeError as e:
        return Response(status=400, response=f'Error reading Markdown in UTF-8: {e}')

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
