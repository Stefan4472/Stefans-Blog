import typing
import click
import pathlib
from renderer import  markdown as md2
from sitemanager import manager
from sitemanager.postconfig import read_config_file, write_config_file
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
    _upload_post(
        path,
        host,
        key,
        allow_update,
        publish,
        feature,
        upload_images,
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
    manager.set_config(config, host, key)
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
                True,
            )
    click.echo('Done')


def _upload_post(
        path: str,
        host: str,
        key: str,
        allow_update: bool,
        publish: bool,
        feature: typing.Optional[bool],
        upload_images: bool,
):
    # Get paths to the Markdown and config files
    path = pathlib.Path(path)
    md_path = path / 'post.md'
    config_path = path / 'post-meta.json'

    # Read the config file
    config = read_config_file(config_path)
    config.publish = publish
    config.feature = feature

    with open(md_path, encoding='utf-8', errors='strict') as f:
        markdown = f.read()

    # Retrieve the list of images referenced in the Markdown and
    # resolve their absolute paths.
    img_paths = [(md_path.parent / local_path).resolve() for local_path in md2.find_images(markdown)]

    # Upload
    manager.upload_post(
        config,
        markdown,
        img_paths,
        allow_update,
        upload_images,
        host,
        key,
    )

    # Write out config (may have been modified)
    write_config_file(config, config_path)


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


@cli.command()
@click.option('--host', type=str, default='http://127.0.0.1:5000', help='Base URL of the site instance')
@click.option('--key', type=str, required=True, help='Your API key')
def get_featured(
        host: str,
        key: str,
):
    """List the featured posts."""
    manager.get_featured(host, key)
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
    manager.set_featured(slug, featured, host, key)
    click.echo('Done')


# Sync a to b
@cli.command()
def sync():
    # TODO
    return


if __name__ == '__main__':
    cli()
