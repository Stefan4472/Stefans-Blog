import pathlib
import typing
import hashlib
from sitemanager import util
from sitemanager.postconfig import PostConfig
from sitemanager.manager_service import ManagerService
import renderer.markdown as md
# from manifest import Manifest
# TODO: EXCEPTIONS


# TODO: THE DIFFING STUFF. WOULD NEED TO ALSO INCLUDE CONFIGS
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

    if upload_images:
        print('Uploading featured image {}...'.format(config.featured_img))
        config.featured_img = pathlib.Path(service.upload_image(config.featured_img))
        print('Uploading banner image {}...'.format(config.banner_img))
        config.banner_img = pathlib.Path(service.upload_image(config.banner_img))
        print('Uploading thumbnail image {}...'.format(config.thumbnail_img))
        config.thumbnail_img = pathlib.Path(service.upload_image(config.thumbnail_img))

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
    service.set_config(config.slug, config)


def set_config(
        config: PostConfig,
        host: str,
        key: str,
):
    service = ManagerService(host, key)
    service.set_config(config.slug, config)


def delete_post(
        slug: str,
        host: str,
        key: str,
):
    service = ManagerService(host, key)
    service.delete_post(slug)


def get_featured(
        host: str,
        key: str,
) -> typing.List[str]:
    service = ManagerService(host, key)
    return service.get_featured()


def set_featured(
        slug: str,
        is_featured: bool,
        host: str,
        key: str,
) -> typing.List[str]:
    service = ManagerService(host, key)
    return service.set_featured(slug, is_featured)


def upload_image(
        path: pathlib.Path,
        host: str,
        key: str,
):
    service = ManagerService(host, key)
    return service.upload_image_new(path)


def delete_image(
        filename: str,
        host: str,
        key: str,
):
    service = ManagerService(host, key)
    return service.delete_image_new(filename)