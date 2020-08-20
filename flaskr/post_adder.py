import pathlib
import typing
from flask import current_app, url_for
from flask.cli import with_appcontext
import flaskr.manifest as mn
import flaskr.manage_util as util
import flaskr.search_engine as se
import flaskr.database as db


@with_appcontext
def add_post(
        post_path: pathlib.Path, 
        quiet: bool,
):
    """Performs the multi-step process of adding a post to the local site
    instance.
    
    In order:
    - Read the metadata file 
    - Render the markdown
    - ...
    """
    # Create pathlib objects
    static_path = pathlib.Path(current_app.static_folder)
    manifest_path = pathlib.Path(current_app.config['MANIFEST_PATH'])
    database_path = pathlib.Path(current_app.config['DATABASE_PATH'])
    search_index_path = pathlib.Path(current_app.config['SEARCH_INDEX_PATH'])

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
    post_html, post_img_paths = util.render_markdown_file(
        md_path,
        post_data.slug,
    )
    post_data.html = post_html

    # Load post images into memory
    post_images = util.process_post_images(
        post_path,
        static_path,
        post_img_paths,
    )
    post_data.images = post_images

    # TODO: HOW TO GET URL TO THE POST'S STATIC DIRECTORY WITHOUT HARDCODING?
    # url_for REQUIRES THE REQUEST CONTEXT
    post_static_url = '/' + 'static' + '/' + post_data.slug
    post_static_rel_path = 'static' + '/' + post_data.slug
    
    # Add post to database
    util.add_post_to_database(
        post_static_url,
        database_path,
        post_data,
    )

    # Compute hashes
    files_to_add = mn.prepare_files_for_add(post_data, post_static_rel_path)
    print(files_to_add)

    # Get diff
    manifest = mn.Manifest(manifest_path)
    post_diff = manifest.calc_addpost_diff(post_data.slug, files_to_add)
    print(post_diff)
    
    if post_diff.write_files:
        print('Files that will be written:')
        for manifest_file in post_diff.write_files:
            print('\t-{}'.format(manifest_file.filename))
    else:
        print('No files need to be written')

    if post_diff.del_files:
        print('Files that will be deleted:')
        for manifest_file in post_diff.del_files:
            print('\t-{}'.format(manifest_file.filename))
    else:
        print('No files need to be deleted')

    manifest.apply_addpost_diff(post_diff, files_to_add, static_path)

    # Add Markdown file to the search engine's index
    search_index = se.index.connect(str(search_index_path))
    search_index.index_file(str(md_path), post_data.slug)
    search_index.commit()
