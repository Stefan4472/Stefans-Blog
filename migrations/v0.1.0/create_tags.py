import json
import sys
from pathlib import Path

import click
import stefan_on_software_api_client.api.tags.get_tags as api_get_tags
import stefan_on_software_api_client.api.tags.post_tags as api_create_tag
import stefan_on_software_api_client.api.tags.put_tags_tag as api_update_tag
from stefan_on_software_api_client import client_util
from stefan_on_software_api_client.models.post_tags_json_body import PostTagsJsonBody
from stefan_on_software_api_client.models.put_tags_tag_json_body import (
    PutTagsTagJsonBody,
)
from stefan_on_software_api_client.types import UNSET, HTTPStatus


@click.command()
@click.argument(
    "tags_path",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
)
@click.option("--email", required=True)
@click.password_option(required=True)
@click.option("--host_url", required=True)
def create_tags(tags_path: Path, email: str, password: str, host_url: str):
    """
    Bulk-create tags on the server.

    TAGS_PATH: path to a JSON file defining the tags to create.
    """
    with open(tags_path) as f:
        tags_json = json.load(f)

    client = client_util.make_client(host_url, email, password)

    # Build dictionary of tags as they exist on the server, mapped by slug.
    online_tags_resp = api_get_tags.sync_detailed(client=client)
    if online_tags_resp.status_code != HTTPStatus.OK:
        click.echo(f"Request to get tags failed with status {online_tags_resp}")
        exit(1)
    online_tags = {
        online_tag.slug: online_tag for online_tag in online_tags_resp.parsed
    }

    # Record slugs of tags that failed.
    failures = set()

    for tag in tags_json["tags"]:
        slug = tag["slug"]
        name = tag["name"]
        description = tag["description"]
        color = tag.get("color")

        if slug in online_tags:
            # Update
            online_tag = online_tags[slug]
            if (
                name == online_tag.name
                and description == online_tag.description
                and (color is None or color == online_tag.color)
            ):
                click.echo(f"Tag {slug} is already up to date.")
            else:
                click.echo(f"Updating tag {slug}")
                res = api_update_tag.sync_detailed(
                    slug,
                    client=client,
                    json_body=PutTagsTagJsonBody(
                        name,
                        description,
                        color if color else online_tags[slug].color,
                    ),
                )
                if res.status_code != HTTPStatus.OK:
                    click.echo(f"Request failed with content={res.content}")
                    failures.add(slug)
        else:
            # Create
            click.echo(f"Creating tag {slug}")
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
                click.echo(f"Request failed with content={res.content}", err=True)
                failures.add(slug)

    if failures:
        click.echo(f"Completed with failures: {failures}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    create_tags()
