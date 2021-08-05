import pathlib
import typing
import hashlib
import util
from post import PostConfig
from manager_service import ManagerService
from manifest import Manifest
# TODO: EXCEPTIONS


def upload_post(
        host: str,
        config: PostConfig,
        html: str,
        images: typing.List[pathlib.Path],
        # update: bool = False,
):
    service = ManagerService(host)
    manifest = service.get_manifest()
    print(manifest.posts)
    diff = manifest.calc_post_diff(config.slug, html, images)
    print(diff)
    service.apply_diff(diff)
    # TODO: WHERE TO HANDLE `PUBLISH` AND `FEATURED`?


def delete_post(host: str, slug: str):
    service = ManagerService(host)
    service.delete_post(slug)
