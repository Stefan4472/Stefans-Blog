import hashlib
import datetime
import flask
import shutil
from flask import request, Response, current_app
from flask_login import login_required
from PIL import Image
import werkzeug.exceptions
import werkzeug.utils
from flaskr.database import db
from . import models
from . import util
'''
Note: this API is not fully RESTful due to the challenge of preserving image filenames 
(changing the image name will break the HTML that expects those images to have specific
filenames). I plan to implement in-site drafting, at which point that problem will go 
away.

Post creation process:
- Create post
- Upload HTML
- Upload images
- Set config (including publish=True)

Eventual REST API:
- POST /post -> CREATE, with all config
- PUT /post -> EDIT, with all config
- PATCH /post -> EDIT, without full config
- /files: endpoints for managing files (image AND HTML)
'''
# TODO: Should have a set of Tag endpoints too
# TODO: SETUP TESTING FRAMEWORK


# Blueprint under which all views will be assigned
API_BLUEPRINT = flask.Blueprint('api', __name__, url_prefix='/api/v1/')


@API_BLUEPRINT.route('/posts', methods=['GET'])
@login_required
def get_posts():
    """
    Get posts.

    Query parameters:
    (bool) `featured`: return only posts where is_featured = ?
    (bool) `published`: return only posts where is_published = ?
    """
    # Create query dynamically
    query = models.Post.query
    if 'featured' in request.args:
        # Convert string value to boolean value
        as_bool = (request.args['featured'].lower() == 'true')
        query = query.filter(models.Post.is_featured == as_bool)
    if 'published' in request.args:
        as_bool = (request.args['published'].lower() == 'true')
        query = query.filter(models.Post.is_published == as_bool)

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


@API_BLUEPRINT.route('/posts/<string:slug>', methods=['POST'])
@login_required
def create_post(slug: str):
    """
    Creates an empty post with the specified slug.

    Returns 400 if a post with the given slug already exists.
    """
    post = models.Post.query.filter_by(slug=slug).first()
    if post:
        msg = 'A post with the given slug already exists'
        return Response(response=msg, status=400)
    post = models.Post(slug=slug)
    db.session.add(post)
    db.session.commit()
    post.get_path().mkdir(exist_ok=True)
    return Response(status=200)


@API_BLUEPRINT.route('/posts/<string:slug>', methods=['DELETE'])
@login_required
def delete_post(slug: str):
    post = models.Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)
    # Delete files, then delete record from DB
    shutil.rmtree(post.get_path())
    models.Post.query.filter_by(slug=slug).delete()
    db.session.commit()
    return Response(status=200)


@API_BLUEPRINT.route('/posts/<string:slug>/config', methods=['POST'])
@login_required
def set_config(slug: str):
    post = models.Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)
    config = request.get_json()
    if 'title' in config:
        post.title = config['title']
    if 'byline' in config:
        post.byline = config['byline']
    if 'date' in config:
        post.date = datetime.datetime.strptime(config['date'], "%m/%d/%y").date()
    if 'image' in config:
        featured_filename = config['image']
        if featured_filename != post.featured_filename:
            find_index = post.find_image(featured_filename)
            if find_index == -1:
                msg = 'Specified image "{}" not found on server'.format(featured_filename)
                return Response(response=msg, status=400)
            else:
                image = post.images[find_index]
                image_path = post.get_path() / image.filename
                img = Image.open(image_path)
                if (img.width, img.height) != (1000, 540):
                    msg = 'Specified image "{}" has the wrong dimensions'.format(featured_filename)
                    return Response(response=msg, status=400)
            post.featured_filename = config['image']
    if 'thumbnail' in config:
        thumbnail_filename = config['thumbnail']
        if thumbnail_filename != post.thumbnail_filename:
            find_index = post.find_image(thumbnail_filename)
            if find_index == -1:
                msg = 'Specified image "{}" not found on server'.format(thumbnail_filename)
                return Response(response=msg, status=400)
            else:
                image = post.images[find_index]
                image_path = post.get_path() / image.filename
                img = Image.open(image_path)
                if (img.width, img.height) != (400, 400):
                    msg = 'Specified image "{}" has the wrong dimensions'.format(thumbnail_filename)
                    return Response(response=msg, status=400)
            post.thumbnail_filename = config['thumbnail']
    if 'banner' in config:
        banner_filename = config['banner']
        if banner_filename != post.banner_filename:
            find_index = post.find_image(banner_filename)
            if find_index == -1:
                msg = 'Specified image "{}" not found on server'.format(banner_filename)
                return Response(response=msg, status=400)
            else:
                image = post.images[find_index]
                image_path = post.get_path() / image.filename
                img = Image.open(image_path)
                if (img.width, img.height) != (1000, 175):
                    msg = 'Specified image "{}" has the wrong dimensions'.format(banner_filename)
                    return Response(response=msg, status=400)
            post.banner_filename = config['banner']
    if 'tags' in config:
        # Add tags
        for tag_name in config['tags']:
            tag_slug = util.generate_slug(tag_name)
            # Lookup tag in the database
            tag = models.Tag.query.filter_by(slug=tag_slug).first()
            # Create tag if doesn't exist already
            if not tag:
                tag = models.Tag(
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
    db.session.commit()
    return Response(status=200)


@API_BLUEPRINT.route('/posts/<string:slug>/body', methods=['POST'])
@login_required
def upload_html(slug: str):
    """Upload the HTML body of the post."""
    post = models.Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)

    # Calculate hash
    file = request.files['file']
    raw = file.read()
    md5 = hashlib.md5(raw).hexdigest()
    file.close()

    # TODO: MODIFICATIONS NEEDED TO SEARCH_ENGINE
    # Add Markdown file to the search engine's index
    # current_app.search_engine.index_file(str(md_path), post_data.slug)
    # current_app.search_engine.commit()

    # Save as 'post.html' if hash is different from current post hash
    if md5 != post.hash:
        file_path = post.get_path() / 'post.html'
        with open(file_path, 'wb+') as writef:
            writef.write(raw)
        # Update hash
        post.hash = md5
        db.session.commit()
    return Response(status=200)


@API_BLUEPRINT.route('/posts/<string:slug>/images', methods=['POST'])
@login_required
def upload_image(slug: str):
    """Upload a single image to the specified post."""
    post = models.Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)

    file = request.files['file']
    # TODO: safe_filename = werkzeug.utils.secure_filename(file.filename)
    file_path = post.get_path() / file.filename

    # Read image, hash, and save to post directory
    raw_img = file.read()
    md5 = hashlib.md5(raw_img).hexdigest()
    file.close()

    found_index = post.find_image(file.filename)
    # No image found with same filename
    if found_index == -1:
        # Add to database
        post.images.append(models.PostImage(
            filename=file.filename,
            hash=md5,
        ))
        # Save
        with open(file_path, 'wb+') as writef:
            writef.write(raw_img)
    # Image found with same filename but different hash (replace)
    elif post.images[found_index].hash != md5:
        post.images[found_index].hash = md5
        # Overwrite
        with open(file_path, 'wb+') as writef:
            writef.write(raw_img)
    # Image found with same filename and same hash: do nothing
    else:
        pass
    db.session.commit()
    return Response(status=200)


@API_BLUEPRINT.route('/posts/<string:slug>/images/<string:filename>', methods=['DELETE'])
@login_required
def delete_image(slug: str, filename: str):
    post = models.Post.query.filter_by(slug=slug).first()
    if not post:
        return Response(status=404)
    found_index = post.find_image(filename)
    if found_index == -1:
        return Response(status=404)
    else:
        image = post.images[found_index]
        # Remove from DB
        # post.images = post.images[:found_index] + post.images[found_index+1:]
        models.PostImage.query.filter_by(post_id=post.id, filename=image.filename).delete()
        # Delete file
        (post.get_path() / image.filename).unlink()
        db.session.commit()
    return Response(status=200)