import pathlib
import typing
import manager_service as ms
from post import PostConfig
# TODO: EXCEPTIONS


def upload_post(
        host: str,
        config: PostConfig,
        html: str,
        images: typing.List[pathlib.Path],
        # update: bool = False,
):
    service = ms.ManagerService(host)
    # TODO: GET MANIFEST AND FIGURE OUT WHAT NEEDS TO BE DONE, THEN DO IT
    # Compute hashes
    # files_to_add = mn.prepare_files_for_add(post_data, post_static_rel_path)
    # Get diff
    # post_diff = current_app.manifest.calc_addpost_diff(post_data.slug, files_to_add)
    # print('Identified {} files to write and {} files to delete'.format(
    #     len(post_diff.write_files),
    #     len(post_diff.del_files),
    # ))

    # current_app.manifest.apply_addpost_diff(
    #     post_diff,
    #     files_to_add,
    #     static_path,
    # )


def delete_post(host: str, slug: str):
    print('Deleting...')
    service = ms.ManagerService(host)
    service.delete_post(slug)
