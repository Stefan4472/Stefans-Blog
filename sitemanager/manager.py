import pathlib
import typing
import hashlib
import util
from postconfig import PostConfig
from managerservice import ManagerService
# from manifest import Manifest
# TODO: EXCEPTIONS


# TODO: THE DIFFING STUFF. WOULD NEED TO ALSO INCLUDE CONFIGS
def upload_post(
        config: PostConfig,
        html: str,
        images: typing.List[pathlib.Path],
        allow_update: bool,
        host: str,
        key: str,
):
    service = ManagerService(host, key)
    manifest = service.get_manifest()

    # No post with given slug exists: create new
    if config.slug not in manifest.posts:
        service.create_post(config.slug)
    # Throw error if a post with given slug exists but `update` is not set to True
    elif not allow_update:
        raise ValueError('Post with the specified slug already exists but update=False')

    print('Uploading HTML...')
    service.upload_html(config.slug, html)
    print('Uploading featured image {}...'.format(config.featured_img))
    service.upload_image(config.slug, config.featured_img)
    print('Uploading banner image {}...'.format(config.banner_img))
    service.upload_image(config.slug, config.banner_img)
    print('Uploading thumbnail image {}...'.format(config.thumbnail_img))
    service.upload_image(config.slug, config.thumbnail_img)
    for image in images:
        print('Uploading image {}...'.format(image))
        service.upload_image(config.slug, image)
    print('Setting config...')
    service.set_config(config.slug, config)


def delete_post(
        slug: str,
        host: str,
        key: str,
):
    service = ManagerService(host, key)
    service.delete_post(slug)
