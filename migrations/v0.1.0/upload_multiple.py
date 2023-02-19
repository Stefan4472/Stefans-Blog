import datetime as dt
import subprocess
import sys
from pathlib import Path

import click
import stefan_on_software_api_client.api.commands.post_commands_publish as api_publish_post
import stefan_on_software_api_client.api.posts.get_posts as api_get_posts
from stefan_on_software_api_client import client_util
from stefan_on_software_api_client.models.post_commands_publish_json_body import (
    PostCommandsPublishJsonBody,
)
from stefan_on_software_api_client.types import HTTPStatus


# TODO: this script has a lot of room for improvement. For now it's just quick-n-dirty.
# TODO: 'dry_run' flag that just validates the posts but doesn't upload anything
@click.command()
@click.argument(
    "posts_path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
)
@click.option("--email", required=True)
@click.password_option(required=True)
@click.option("--host_url", required=True)
def migrate(posts_path: Path, email: str, password: str, host_url: str):
    # Get the path to the upload.py script. This is a very quick hack for now.
    upload_script = (
        Path(__file__).parent.parent.parent
        / "stefan-on-software-api-client"
        / "bin"
        / "upload.py"
    ).absolute()

    client = client_util.make_client(host_url, email, password)
    for post_dir in posts_path.iterdir():
        if not post_dir.is_dir() or post_dir.name.startswith("_"):
            click.echo(f"Skipping {post_dir.resolve()}")
            continue
        try:
            # print(post_dir)
            post = client_util.load_post(post_dir)
            click.echo(f"Uploading post {post.metadata.slug}")
            # TODO: pull creation code into utility function so we can call it from here *and* get the post ID without needing a second API call.
            res = subprocess.run(
                [
                    sys.executable,
                    str(upload_script),
                    str(post_dir.absolute()),
                    f"--email={email}",
                    f"--password={password}",
                    f"--host_url={host_url}",
                ],
                capture_output=True,
            )
            if res.returncode:
                click.echo(
                    f"Error running upload for post {post.metadata.slug}: {res.stderr}"
                )

            # Get the ID of the newly-created post.
            # TODO: this is incredibly inefficient and a bad hack for now.
            res_get = api_get_posts.sync_detailed(client=client, limit=100, offset=0)
            if res_get.status_code != HTTPStatus.OK:
                click.echo("Request failed")
            this_post = [p for p in res_get.parsed if p.slug == post.metadata.slug][0]

            publish_date = dt.datetime.combine(post.metadata.date, dt.time.min)
            res_publish = api_publish_post.sync_detailed(
                client=client,
                json_body=PostCommandsPublishJsonBody(
                    this_post.id,
                    False,
                    publish_date=str(publish_date),
                ),
            )
            if res_publish.status_code != HTTPStatus.NO_CONTENT:
                click.echo(f"Request failed with content={res_publish.content}")

        except ValueError as e:
            print(post_dir.resolve())
            click.echo(e, err=True)


if __name__ == "__main__":
    migrate()
