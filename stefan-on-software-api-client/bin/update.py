import sys
from pathlib import Path

import click
import stefan_on_software_api_client.api.posts.post_posts_post_id_content as api_set_post_content
import stefan_on_software_api_client.api.posts.put_posts_post_id as api_update_post
from stefan_on_software_api_client import client_util
from stefan_on_software_api_client.models.post_posts_post_id_content_multipart_data import (
    PostPostsPostIdContentMultipartData,
)
from stefan_on_software_api_client.models.put_posts_post_id_json_body import (
    PutPostsPostIdJsonBody,
)
from stefan_on_software_api_client.types import UNSET
from stefan_on_software_api_client.types import File as UploadFile
from stefan_on_software_api_client.types import HTTPStatus
from stefan_on_software_renderer import renderer


# TODO: needs significant revisions and error-handling.
# TODO: repeated code with upload.py
@click.command()
@click.argument("post_id", type=int)
@click.argument(
    "path", type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path)
)
@click.option("--email", required=True)
@click.password_option(required=True)
@click.option("--host_url", required=True)
def update_post(post_id: int, path: Path, email: str, password: str, host_url: str):
    """
    Update the Markdown (and upload all images) for a given post.

    POST_ID: the ID of the post to update.
    """
    try:
        post = client_util.load_post(path)
    except ValueError as e:
        click.echo(e, err=True)
        sys.exit(1)

    client = client_util.make_client(host_url, email, password)

    # TODO: should file upload reject duplicates explicitly?
    featured_path = (path / post.metadata.image).resolve()
    click.echo(f"Uploading featured image {featured_path}...")
    with open(featured_path, mode="rb") as contents:
        featured_id = client_util.upload_file(
            client, UploadFile(contents, featured_path.name)
        ).id

    banner_path = (path / post.metadata.banner).resolve()
    click.echo(f"Uploading banner image {banner_path}...")
    with open(banner_path, mode="rb") as contents:
        banner_id = client_util.upload_file(
            client, UploadFile(contents, banner_path.name)
        ).id

    thumbnail_path = (path / post.metadata.thumbnail).resolve()
    click.echo(f"Uploading thumbnail image {thumbnail_path}...")
    with open(thumbnail_path, mode="rb") as contents:
        thumbnail_id = client_util.upload_file(
            client, UploadFile(contents, thumbnail_path.name)
        ).id

    click.echo("Updating post...")
    res_update = api_update_post.sync_detailed(
        post_id,
        client=client,
        json_body=PutPostsPostIdJsonBody(
            slug=post.metadata.slug if post.metadata.slug else UNSET,
            title=post.metadata.title if post.metadata.title else UNSET,
            byline=post.metadata.byline if post.metadata.byline else UNSET,
            featured_image=featured_id if featured_id else UNSET,
            banner_image=banner_id if banner_id else UNSET,
            thumbnail_image=thumbnail_id if thumbnail_id else UNSET,
        ),
    )
    if res_update.status_code != HTTPStatus.OK:
        click.echo(f"Request failed with content={res_update.content}", err=True)
        sys.exit(1)

    with open(post.md_path, encoding="utf-8", errors="strict") as markdown_file:
        post_md = markdown_file.read()
    # Get the list of image filenames referenced in the Markdown
    for filename in renderer.find_images(post_md):
        # Resolve absolute path
        full_path = (path / filename).resolve()
        # Upload image and get its online filename
        click.echo(f"Uploading image {full_path}...")
        with open(full_path, mode="rb") as contents:
            # TODO: not sure if this will work correctly
            new_filename = client_util.upload_file(
                client, UploadFile(contents, full_path.name)
            ).filename
            # Update Markdown to use the new filename TODO: the naive find-and-replace is risky!
            post_md = post_md.replace(filename, new_filename)

    click.echo("Uploading Markdown...")
    res_content = api_set_post_content.sync_detailed(
        post_id,
        client=client,
        multipart_data=PostPostsPostIdContentMultipartData(
            UploadFile(post_md, "post.md")
        ),
    )
    if res_content.status_code != HTTPStatus.NO_CONTENT:
        click.echo(f"Request failed with content={res_content.content}")
        sys.exit(1)


if __name__ == "__main__":
    update_post()
