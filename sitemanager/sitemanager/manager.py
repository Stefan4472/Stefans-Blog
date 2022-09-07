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
# TODO: HANDLE POSSIBLE EXCEPTIONS


# TODO: this has too many arguments. Provide an `Options` dataclass?
def upload_post_from_dir(
        path: pathlib.Path,
        host: str,
        email: str,
        password: str,
        allow_update: bool,
        publish: bool,
        feature: typing.Optional[bool],
        upload_images: bool,
        send_email: bool,
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
            config, markdown, allow_update, upload_images, send_email, path, host, email, password
        )

        # Write out config (may have been modified)
        write_config_file(config, config_path)


def upload_post(
        config: PostConfig,
        markdown: str,
        allow_update: bool,
        upload_images: bool,
        send_email: bool,
        base_path: pathlib.Path,
        host: str,
        email: str,
        password: str,
):
    service = ManagerService(host, email, password)
    manifest = service.get_manifest()

    # Check `allow_update` condition before we do a lot of work
    if config.slug in manifest.posts and not allow_update:
        msg = 'Post with the specified slug already exists but update=False'
        raise ValueError(msg)

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
            # Update Markdown to use the new filename TODO: the naive find-and-replace is risky!
            markdown = markdown.replace(filename, new_filename)

    # Use PUT if post already exists, else POST
    if config.slug in manifest.posts:
        print('Updating post...')
        service.update_post(new_config)
    else:
        print('Creating post...')
        service.create_post(new_config, send_email)

    print('Uploading Markdown...')
    service.upload_markdown(config.slug, markdown)
