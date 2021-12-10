import pathlib
import typing
import hashlib
import copy
from sitemanager import util
from sitemanager.postconfig import PostConfig
from sitemanager.manager_service import ManagerService
from sitemanager.postconfig import read_config_file, write_config_file
import renderer.markdown as md
"""Multi-step functionality using `ManagerService`."""
# TODO: HANDLE EXCEPTIONS
# TODO: THE DIFFING/SYNCING STUFF? WOULD BE FUN TO IMPLEMENT BUT NOT USEFUL


def upload_post_from_dir(
        path: pathlib.Path,
        host: str,
        key: str,
        allow_update: bool,
        publish: bool,
        feature: typing.Optional[bool],
        upload_images: bool,
):
        # Get paths to the Markdown and config files
        path = pathlib.Path(path)
        md_path = path / 'post.md'
        config_path = path / 'post-meta.json'

        # Read the config file
        config = read_config_file(config_path)
        config.publish = publish
        config.feature = feature

        with open(md_path, encoding='utf-8', errors='strict') as f:
            markdown = f.read()

        upload_post(
            config, markdown, allow_update, upload_images, path, host, key,
        )

        # Write out config (may have been modified)
        write_config_file(config, config_path)


def upload_post(
        config: PostConfig,
        markdown: str,
        allow_update: bool,
        upload_images: bool,
        base_path: pathlib.Path,
        host: str,
        key: str,
):
    service = ManagerService(host, key)
    manifest = service.get_manifest()

    # No post with given slug exists: create new
    if config.slug not in manifest.posts:
        print('Creating post...')
        service.create_post(config.slug)
    # Throw error if a post with given slug exists but `update` is not set to True
    elif not allow_update:
        raise ValueError('Post with the specified slug already exists but update=False')

    new_config = copy.copy(config)
    if upload_images:
        print('Uploading featured image {}...'.format(config.featured_img))
        new_config.featured_img = pathlib.Path(service.upload_image(config.featured_img))
        print('Uploading banner image {}...'.format(config.banner_img))
        new_config.banner_img = pathlib.Path(service.upload_image(config.banner_img))
        print('Uploading thumbnail image {}...'.format(config.thumbnail_img))
        new_config.thumbnail_img = pathlib.Path(service.upload_image(config.thumbnail_img))

        # Get the list of image filenames referenced in the Markdown
        for filename in md.find_images(markdown):
            # Resolve absolute path
            full_path = (base_path / filename).resolve()
            # Upload image and get its online filename
            print('Uploading image {}...'.format(full_path))
            new_filename = service.upload_image(full_path)
            # Update Markdown in-memomry to use the new filename
            markdown = md.replace_image(markdown, filename, new_filename)
    print('Uploading Markdown...')
    service.upload_markdown(config.slug, markdown)
    print('Setting config...')
    service.set_config(config.slug, new_config)


# def apply_diff(self, diff: SiteDiff):
#     for create_slug in diff.create_posts:
#         self.create_post(create_slug)
#     for delete_slug in diff.delete_posts:
#         self.delete_post(delete_slug)
#     for post_diff in diff.post_diffs:
#         if post_diff.write_html:
#             print('Uploading HTML')
#             self.upload_html(post_diff.slug, post_diff.write_html)
#         for upload in post_diff.write_images:
#             print('Uploading {}'.format(upload))
#             self.upload_image(post_diff.slug, upload)
#         for delete in post_diff.delete_images:
#             print('Deleting {}'.format(delete))
#             self.delete_image(post_diff.slug, delete)
