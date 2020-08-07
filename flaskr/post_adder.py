import pathlib
import typing
from flaskr.manifest import Manifest
import flaskr.manage_util as util


class PostAdder:
    """Performs the multi-step process of adding a post to the local site
    instance."""
    def add_post(
            self,
            post_path: pathlib.Path, 
            static_path: pathlib.Path,
            manifest_path: pathlib.Path,
            database_path: pathlib.Path,
            quiet: bool,
    ):
        if not quiet:
            print('Adding post from directory "{}"'.format(post_path))
    
        # Determine absolute paths to the Markdown and metadata files
        self.md_path = post_path / 'post.md'
        self.meta_path = post_path / 'post-meta.json'

        # Read the metadata file
        post_json = util.read_meta_file(self.meta_path)

        # Process metadata
        self.post_data = util.process_post_meta(post_path, post_json)

        # Determine where the post data will live on this site's staticpath
        self.post_static_path = static_path / self.post_data.slug

        # Render Markdown file, getting the HTML and sourced images
        self.post_html, post_img_paths = util.render_markdown_file(
            self.md_path,
            self.post_static_path,
        )

        # Load post images into memory
        self.post_images = util.process_post_images(
            post_path,
            static_path,
            post_img_paths,
        )

        # Add post to database
        util.add_post_to_database(database_path, self.post_data)


        # Get connection to manifest and determine what needs to 
        # be done on disk
        # manifest = Manifest(manifest_path)
        # diff = manifest.calculate_diff(self.post_meta.slug, self.post_data)

        # if not quiet:
        #     print('Will add {} files, delete {} files, and overwrite {} files'\
        #         .format(len(diff.add_files), len(diff.rmv_files), 
        #             len(diff.overwrite_files))

        # # Calculate hashes
        # self.html_hash = util.calculate_str_hash(self.post_html)
        # self.featured_img_hash = \
        #     util.calculate_img_hash(self.post_meta.featured_img)

        # self.hashes = util.calculate_hashes(

