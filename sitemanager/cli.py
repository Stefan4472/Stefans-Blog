import typing

import click
import pathlib
import manager
import markdown
from postconfig import PostConfig
# CLI interface


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--key', type=str, required=True, help='Your API key')
@click.option('--allow_update', type=bool, default=False, help='Whether to allow updating an already-existing post. If this is set to False, and a post with the given slug already exists, an Exception will be thrown')
@click.option('--publish', type=bool, default=True, help='Whether to publish the post once upload is finished')
@click.option('--feature', type=bool, help='Whether to mark the post as "featured" once upload is finished')
def upload_post(
        path: str,
        host: str,
        key: str,
        allow_update: bool,
        publish: bool,
        feature: typing.Optional[bool],
):
    _upload_post(
        path,
        host,
        key,
        allow_update,
        publish,
        feature,
    )
    click.echo('Done')


@cli.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--key', type=str, required=True, help='Your API key')
@click.option('--allow_update', type=bool, default=False, help='Whether to allow updating an already-existing post. If this is set to False, and a post with the given slug already exists, an Exception will be thrown')
@click.option('--publish', type=bool, default=True, help='Whether to publish (all) the posts once upload is finished')
def upload_posts(
        path: str,
        host: str,
        key: str,
        allow_update: bool,
        publish: bool,
):
    """
    Upload multiple posts at once. PATH is a file that contains a list of
    post directories, one per line.
    """
    with open(path, 'r') as post_file:
        for line in post_file:
            click.echo('Uploading post from {}'.format(pathlib.Path(line.strip()).resolve()))
            _upload_post(
                line.strip(),
                host,
                key,
                allow_update,
                publish,
                None,
            )
    click.echo('Done')


def _upload_post(
        path: str,
        host: str,
        key: str,
        allow_update: bool,
        publish: bool,
        feature: typing.Optional[bool],
):
    # Get paths to the Markdown and config files
    path = pathlib.Path(path)
    md_path = path / 'post.md'
    config_path = path / 'post-meta.json'

    # Read the config file
    config = PostConfig.from_file(config_path)
    config.publish = publish
    config.feature = feature

    # Render Markdown file, getting the HTML and sourced images
    html, post_img_paths = markdown.render_file(
        md_path,
        config.slug,
    )

    # Upload
    manager.upload_post(
        config,
        html,
        post_img_paths,
        allow_update,
        host,
        key,
    )


@cli.command()
@click.argument('slug', type=str)
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--key', type=str, required=True, help='Your API key')
def delete_post(
        slug: str,
        host: str,
        key: str,
):
    """Delete post with the given SLUG from the site."""
    manager.delete_post(slug, host, key)
    click.echo('Done')


# Sync a to b
@cli.command()
def sync():
    # TODO
    return


if __name__ == '__main__':
    cli()
