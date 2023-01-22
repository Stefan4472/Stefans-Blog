"""CLI interface for several commonly-used management functions using the StefanOnSoftware API."""
from typing import Optional

import click
import stefan_on_software_api_client.api.commands.post_commands_feature as api_feature_post
import stefan_on_software_api_client.api.commands.post_commands_publish as api_publish_post
import stefan_on_software_api_client.api.commands.post_commands_unfeature as api_unfeature_post
import stefan_on_software_api_client.api.commands.post_commands_unpublish as api_unpublish_post
import stefan_on_software_api_client.api.posts.delete_posts_post_id as api_delete_post
import stefan_on_software_api_client.api.tags.delete_tags_tag as api_delete_tag
import stefan_on_software_api_client.api.tags.post_tags as api_create_tag
import stefan_on_software_api_client.api.tags.put_tags_tag as api_update_tag
from stefan_on_software_api_client import client_util
from stefan_on_software_api_client.models.post_commands_feature_json_body import (
    PostCommandsFeatureJsonBody,
)
from stefan_on_software_api_client.models.post_commands_publish_json_body import (
    PostCommandsPublishJsonBody,
)
from stefan_on_software_api_client.models.post_commands_unfeature_json_body import (
    PostCommandsUnfeatureJsonBody,
)
from stefan_on_software_api_client.models.post_commands_unpublish_json_body import (
    PostCommandsUnpublishJsonBody,
)
from stefan_on_software_api_client.models.post_tags_json_body import PostTagsJsonBody
from stefan_on_software_api_client.models.put_tags_tag_json_body import (
    PutTagsTagJsonBody,
)
from stefan_on_software_api_client.types import UNSET, HTTPStatus


@click.group()
def cli():
    pass


# TODO: these commands will be executed by humans; should probably use post slugs instead
# TODO: detailed readme with example commands
@cli.command()
@click.argument("post_id", type=int)
@click.option("--send_email", required=True, type=bool)
@click.option(
    "--email", required=True, help="Email address used to authenticate with the API"
)
@click.password_option(required=True)
@click.option(
    "--host_url",
    required=True,
    help="Host URL of the site instance, e.g. http://localhost:5000",
)
def publish_post(
    post_id: int,
    send_email: bool,
    email: str,
    password: str,
    host_url: str,
):
    """
    Publish a post.

    POST_ID: ID of the post to publish.
    SEND_EMAIL: Whether to trigger an email campaign to subscribers.
    """
    client = client_util.make_client(host_url, email, password)
    res = api_publish_post.sync_detailed(
        client=client,
        json_body=PostCommandsPublishJsonBody(
            post_id,
            send_email,
        ),
    )
    if res.status_code != HTTPStatus.NO_CONTENT:
        click.echo(f"Request failed with content={res.content}")


@cli.command()
@click.argument("post_id", type=int)
@click.option(
    "--email",
    type=str,
    required=True,
    help="Email address used to authenticate with the API",
)
@click.password_option(required=True)
@click.option(
    "--host_url",
    required=True,
    help="Host URL of the site instance, e.g. http://localhost:5000",
)
def unpublish_post(
    post_id: int,
    email: str,
    password: str,
    host_url: str,
):
    client = client_util.make_client(host_url, email, password)
    res = api_unpublish_post.sync_detailed(
        client=client,
        json_body=PostCommandsUnpublishJsonBody(post_id),
    )
    if res.status_code != HTTPStatus.NO_CONTENT:
        click.echo(f"Request failed with content={res.content}")


@cli.command()
@click.argument("post_id", type=int)
@click.option(
    "--email",
    type=str,
    required=True,
    help="Email address used to authenticate with the API",
)
@click.password_option(required=True)
@click.option(
    "--host_url",
    required=True,
    help="Host URL of the site instance, e.g. http://localhost:5000",
)
def feature_post(
    post_id: int,
    email: str,
    password: str,
    host_url: str,
):
    client = client_util.make_client(host_url, email, password)
    res = api_feature_post.sync_detailed(
        client=client,
        json_body=PostCommandsFeatureJsonBody(post_id),
    )
    if res.status_code != HTTPStatus.NO_CONTENT:
        click.echo(f"Request failed with content={res.content}")


@cli.command()
@click.argument("post_id", type=int)
@click.option(
    "--email",
    type=str,
    required=True,
    help="Email address used to authenticate with the API",
)
@click.password_option(required=True)
@click.option(
    "--host_url",
    required=True,
    help="Host URL of the site instance, e.g. http://localhost:5000",
)
def unfeature_post(
    post_id: int,
    email: str,
    password: str,
    host_url: str,
):
    client = client_util.make_client(host_url, email, password)
    res = api_unfeature_post.sync_detailed(
        client=client,
        json_body=PostCommandsUnfeatureJsonBody(post_id),
    )
    if res.status_code != HTTPStatus.NO_CONTENT:
        click.echo(f"Request failed with content={res.content}")


@cli.command()
@click.argument("post_id", type=int)
@click.option(
    "--email",
    type=str,
    required=True,
    help="Email address used to authenticate with the API",
)
@click.password_option(required=True)
@click.option(
    "--host_url",
    required=True,
    help="Host URL of the site instance, e.g. http://localhost:5000",
)
def delete_post(
    post_id: int,
    email: str,
    password: str,
    host_url: str,
):
    client = client_util.make_client(host_url, email, password)
    res = api_delete_post.sync_detailed(
        post_id,
        client=client,
    )
    if res.status_code != HTTPStatus.NO_CONTENT:
        click.echo(f"Request failed with content={res.content}")


@cli.command()
@click.argument("slug", type=str, required=True)
@click.argument("name", type=str, required=True)
@click.argument("description", type=str, required=True)
@click.option("--color", type=str)
@click.option(
    "--email",
    type=str,
    required=True,
    help="Email address used to authenticate with the API",
)
@click.password_option(required=True)
@click.option(
    "--host_url",
    required=True,
    help="Host URL of the site instance, e.g. http://localhost:5000",
)
def create_tag(
    slug: str,
    name: str,
    description: str,
    color: Optional[str],
    email: str,
    password: str,
    host_url: str,
):
    client = client_util.make_client(host_url, email, password)
    res = api_create_tag.sync_detailed(
        client=client,
        json_body=PostTagsJsonBody(
            name,
            slug,
            description,
            color=color if color else UNSET,
        ),
    )
    if res.status_code != HTTPStatus.CREATED:
        click.echo(f"Request failed with content={res.content}")


@cli.command()
@click.argument("slug", type=str)
@click.argument("name", type=str)
@click.argument("description", type=str)
@click.argument("color", type=str)
@click.option(
    "--email",
    type=str,
    required=True,
    help="Email address used to authenticate with the API",
)
@click.password_option(required=True)
@click.option(
    "--host_url",
    required=True,
    help="Host URL of the site instance, e.g. http://localhost:5000",
)
def update_tag(
    slug: str,
    name: str,
    description: str,
    color: str,
    email: str,
    password: str,
    host_url: str,
):
    client = client_util.make_client(host_url, email, password)
    res = api_update_tag.sync_detailed(
        slug,
        client=client,
        json_body=PutTagsTagJsonBody(
            name,
            description,
            color,
        ),
    )
    if res.status_code != HTTPStatus.OK:
        click.echo(f"Request failed with content={res.content}")


@cli.command()
@click.argument("slug", type=str)
@click.option(
    "--email",
    type=str,
    required=True,
    help="Email address used to authenticate with the API",
)
@click.password_option(required=True)
@click.option(
    "--host_url",
    required=True,
    help="Host URL of the site instance, e.g. http://localhost:5000",
)
def delete_tag(
    slug: str,
    email: str,
    password: str,
    host_url: str,
):
    client = client_util.make_client(host_url, email, password)
    res = api_delete_tag.sync_detailed(
        tag=slug,
        client=client,
    )
    if res.status_code != HTTPStatus.NO_CONTENT:
        click.echo(f"Request failed with content={res.content}")


if __name__ == "__main__":
    cli()
