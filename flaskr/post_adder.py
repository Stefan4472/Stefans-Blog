import os
import pathlib
import typing
from flask import current_app, url_for
from flask.cli import with_appcontext
import flaskr.manifest as mn
import flaskr.manage_util as util
import flaskr.search_engine as se
import flaskr.database as db


class PostAdder:
    """Performs the multi-step process of adding a post to the local site
    instance."""
    # TODO: THIS CAN JUST BE A STAND-ALONE FUNCTION
    @with_appcontext
    def add_post(
            self,
            post_path: pathlib.Path, 
            quiet: bool,
    ):
        # Create pathlib objects
        static_path = pathlib.Path(current_app.static_folder)
        manifest_path = pathlib.Path(current_app.config['MANIFEST_PATH'])
        database_path = pathlib.Path(current_app.config['DATABASE_PATH'])
        sindex_path = pathlib.Path(current_app.config['SEARCH_INDEX_PATH'])

        # Determine absolute paths to the Markdown and metadata files
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
        # util.add_post_to_database(
        #     post_static_url,
        #     database_path,
        #     post_data,
        # )

        # Compute hashes
        files_to_add = mn.prepare_files_for_add(post_data, post_static_rel_path)
        print(files_to_add)
        # # Get diff
        # manifest = mn.Manifest(manifest_path)
        # post_diff = manifest.get_post_diff(post_data.slug, post_hashes)
        # print(post_diff)

        # if not quiet:
        #     print('Will add {} files, delete {} files, and overwrite {} files'\
        #         .format(len(diff.add_files), len(diff.rmv_files), 
        #             len(diff.overwrite_files))

        # Create post's static path
        try:
            os.mkdir(post_static_path)
        except FileExistsError:
            pass

        # Save article html to 'static'
        html_path = post_static_path / (post_data.slug + '.html')
        with open(html_path, 'w', encoding='utf-8', errors='strict') as f:
            f.write(post_html)

        # Save post featured images to 'static'
        post_data.featured_img.image.save(post_static_path / 'featured.jpg')
        post_data.banner_img.image.save(post_static_path / 'banner.jpg')
        post_data.thumbnail_img.image.save(post_static_path / 'thumbnail.jpg')
        
        # Save other post images to 'static'
        for post_image in post_images:
            util.copy_to_static(post_static_path, post_image.path)

        # Add Markdown file to the search engine's index
        search_index = se.index.connect(str(sindex_path))
        search_index.index_file(str(md_path), post_data.slug)
        search_index.commit()


