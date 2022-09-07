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
@click.option('--email', type=str, required=True, help='Email address used to authenticate with the API')
@click.password_option(required=True)
@click.option('--allow_update', type=bool, default=False, help='Whether to allow updating an already-existing post. If this is set to False, and a post with the given slug already exists, an Exception will be thrown')
@click.option('--publish', type=bool, default=True, help='Whether to publish the post once upload is finished')
@click.option('--feature', type=bool, help='Whether to mark the post as "featured" once upload is finished')
@click.option('--upload_images', type=bool, default=True, help='Whether to upload the images referenced in the post')
@click.option('--send_email', type=bool, required=True, help='Whether to send a notification email to subscribers')
def upload_post(
        path: str,
        host: str,
        email: str,
        password: str,
        allow_update: bool,
        publish: bool,
        feature: bool,
        upload_images: bool,
        send_email: bool,
):
    manager.upload_post_from_dir(
        path, host, email, password, allow_update, publish, feature, upload_images, send_email
    )
    click.echo('Done')


@cli.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--email', type=str, required=True, help='Email address used to authenticate with the API')
@click.password_option(required=True)
def set_config(
        path: str,
        host: str,
        email: str,
        password: str,
):
    """Upload the `post-meta.json` config data for the specified post."""
    path = pathlib.Path(path)
    config_path = path / 'post-meta.json'
    config = read_config_file(config_path)
    service = ManagerService(host, email, password)
    service.set_config(config.slug, config)
    click.echo('Done')


@cli.command()
@click.argument('slug', type=str)
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--email', type=str, required=True, help='Email address used to authenticate with the API')
@click.password_option(required=True)
def delete_post(
        slug: str,
        host: str,
        email: str,
        password: str,
):
    """Delete post with the given SLUG from the site."""
    service = ManagerService(host, email, password)
    service.delete_post(slug)
    click.echo('Done')


@cli.command()
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--email', type=str, required=True, help='Email address used to authenticate with the API')
@click.password_option(required=True)
def get_featured(
        host: str,
        email: str,
        password: str,
):
    """List the featured posts."""
    service = ManagerService(host, email, password)
    print(service.get_featured())
    click.echo('Done')


@cli.command()
@click.argument('slug', type=str)
@click.option('--featured', type=bool, required=True)
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--email', type=str, required=True, help='Email address used to authenticate with the API')
@click.password_option(required=True)
def set_featured(
        slug: str,
        featured: bool,
        host: str,
        email: str,
        password: str,
):
    """Toggle whether a specific post is featured."""
    service = ManagerService(host, email, password)
    service.set_featured(slug, featured)
    click.echo('Done')


@cli.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=False, file_okay=True))
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--email', type=str, required=True, help='Email address used to authenticate with the API')
@click.password_option(required=True)
def upload_image(
        path: pathlib.Path,
        host: str,
        email: str,
        password: str,
):
    """Upload the image at PATH to the site."""
    service = ManagerService(host, email, password)
    print(service.upload_image(path))


@cli.command()
@click.argument('filename')
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--email', type=str, required=True, help='Email address used to authenticate with the API')
@click.password_option(required=True)
def delete_image(
        filename: str,
        host: str,
        email: str,
        password: str,
):
    """Delete the image with given filename."""
    service = ManagerService(host, email, password)
    service.delete_image(filename)


if __name__ == '__main__':
    cli()
