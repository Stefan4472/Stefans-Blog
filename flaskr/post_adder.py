import os
import pathlib
import typing
from flaskr.manifest import Manifest
import flaskr.manage_util as util
import flaskr.search_engine as se
import flaskr.database as db


class PostAdder:
    """Performs the multi-step process of adding a post to the local site
    instance."""
    def add_post(
            self,
            post_path: pathlib.Path, 
            static_path: pathlib.Path,
            manifest_path: pathlib.Path,
            database_path: pathlib.Path,
            search_index_path: pathlib.Path,
            quiet: bool,
    ):
        # Determine absolute paths to the Markdown and metadata files
        md_path = post_path / 'post.md'
        meta_path = post_path / 'post-meta.json'

        # Read the metadata file
        post_json = util.read_meta_file(meta_path)

        # Process metadata
        post_data = util.process_post_meta(post_path, post_json)

        # Determine where the post data will live on this site's staticpath
        post_static_path = static_path / post_data.slug

        # Render Markdown file, getting the HTML and sourced images
        post_html, post_img_paths = util.render_markdown_file(
            md_path,
            post_data.slug,
        )

        # Load post images into memory
        post_images = util.process_post_images(
            post_path,
            static_path,
            post_img_paths,
        )

        # TODO: HOW TO GET URL TO THE POST'S STATIC DIRECTORY?
        post_static_url = '/' + 'static' + '/' + post_data.slug

        # Add post to database
        util.add_post_to_database(
            post_static_url,
            database_path,
            post_data,
        )

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
        search_index = se.index.connect(str(search_index_path))
        search_index.index_file(str(md_path), post_data.slug)
        search_index.commit()


        # Get connection to manifest and determine what needs to 
        # be done on disk
        # manifest = Manifest(manifest_path)
        # diff = manifest.calculate_diff(post_meta.slug, post_data)

        # if not quiet:
        #     print('Will add {} files, delete {} files, and overwrite {} files'\
        #         .format(len(diff.add_files), len(diff.rmv_files), 
        #             len(diff.overwrite_files))

        # # Calculate hashes
        # html_hash = util.calculate_str_hash(post_html)
        # featured_img_hash = \
        #     util.calculate_img_hash(post_meta.featured_img)

        # hashes = util.calculate_hashes(

