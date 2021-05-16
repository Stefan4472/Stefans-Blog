import pathlib
import typing
import flask
from flask import current_app
from . import manifest as mn
from . import manage_util as util


@flask.cli.with_appcontext
def add_post(
        post_path: pathlib.Path, 
        quiet: bool,
):
    """Performs the multi-step process of adding a post to the local site
    instance.
    
    In order:
    - Read the metadata file
      - If no images are specified, run `ImageCropper` to have the user select them
    - Render the markdown to HTML
    - Process the images in the post
    - Add the post to the database
    - Check the manifest to see which files need to be added/removed. Perform
      the changes and update the manifest
    - Add the rendered HTML to the search engine index
    """
    # Create pathlib objects
    static_path = pathlib.Path(current_app.static_folder)

    # Get paths to the Markdown and metadata files
    md_path = post_path / 'post.md'
    meta_path = post_path / 'post-meta.json'

    # Read the metadata file
    post_json = util.read_meta_file(meta_path)

    # Process metadata
    post_data = util.process_post_meta(post_path, post_json)

    # Create path where the post data will live on this site's staticpath
    post_static_path = static_path / post_data.slug

    # Render Markdown file, getting the HTML and sourced images
    post_data.html, post_img_paths = util.render_markdown_file(
        md_path,
        post_data.slug,
    )

    # Load post images into memory
    post_data.images = util.process_post_images(
        post_path,
        static_path,
        post_img_paths,
    )

    # TODO: HOW TO GET URL TO THE POST'S STATIC DIRECTORY WITHOUT HARDCODING?
    # url_for REQUIRES THE REQUEST CONTEXT
    post_static_url = '/' + 'static' + '/' + post_data.slug
    post_static_rel_path = 'static' + '/' + post_data.slug
    
    # Add post to database
    util.add_post_to_database(
        post_static_url,
        post_data,
    )

    # Compute hashes
    files_to_add = mn.prepare_files_for_add(post_data, post_static_rel_path)

    # Get diff
    post_diff = current_app.manifest.calc_addpost_diff(post_data.slug, files_to_add)
    
    print('Identified {} files to write and {} files to delete'.format(
        len(post_diff.write_files),
        len(post_diff.del_files),
    ))

    current_app.manifest.apply_addpost_diff(
        post_diff, 
        files_to_add, 
        static_path,
    )

    # Add Markdown file to the search engine's index
    current_app.search_engine.index_file(str(md_path), post_data.slug)
    current_app.search_engine.commit()
