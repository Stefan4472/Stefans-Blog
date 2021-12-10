import typing
import click
import pathlib
from sitemanager import manager
from sitemanager.manager_service import ManagerService
from sitemanager.postconfig import read_config_file, write_config_file
"""CLI interface to the site management API and `manager.py` functionality."""


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
@click.option('--upload_images', type=bool, default=True, help='Whether to upload the images referenced in the post')
def upload_post(
        path: str,
        host: str,
        key: str,
        allow_update: bool,
        publish: bool,
        feature: bool,
        upload_images: bool,
):
    manager.upload_post_from_dir(
        path, host, key, allow_update, publish, feature, upload_images,
    )
    click.echo('Done')


@cli.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--key', type=str, required=True, help='Your API key')
def set_config(
        path: str,
        host: str,
        key: str,
):
    """Upload the `post-meta.json` config data for the specified post."""
    path = pathlib.Path(path)
    config_path = path / 'post-meta.json'
    config = read_config_file(config_path)
    service = ManagerService(host, key)
    service.set_config(config.slug, config)
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
            path = pathlib.Path(line.strip()).resolve()
            click.echo('Uploading post from {}'.format(path))
            manager.upload_post_from_dir(
                path, host, key, allow_update, publish, None, True,
            )
    click.echo('Done')


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
    service = ManagerService(host, key)
    service.delete_post(slug)
    click.echo('Done')


@cli.command()
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--key', type=str, required=True, help='Your API key')
def get_featured(
        host: str,
        key: str,
):
    """List the featured posts."""
    service = ManagerService(host, key)
    print(service.get_featured())
    click.echo('Done')


@cli.command()
@click.argument('slug', type=str)
@click.option('--featured', type=bool, required=True)
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--key', type=str, required=True, help='Your API key')
def set_featured(
        slug: str,
        featured: bool,
        host: str,
        key: str,
):
    """List the featured posts."""
    service = ManagerService(host, key)
    service.set_featured(slug, is_featured)
    click.echo('Done')


@cli.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--key', type=str, required=True, help='Your API key')
def upload_image(
        host: str,
        key: str,
        path: pathlib.Path,
):
    """Upload the image at PATH to the site."""
    service = ManagerService(host, key)
    print(service.upload_image(path))


@cli.command()
@click.argument('filename')
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--key', type=str, required=True, help='Your API key')
def delete_image(
    filename: str,
    host: str,
    key: str,
):
    """Delete the image with given filename."""
    service = ManagerService(host, key)
    service.delete_image(filename)


if __name__ == '__main__':
    cli()
