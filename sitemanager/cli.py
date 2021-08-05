import click
import pathlib
import manager
import markdown
from post import PostConfig
# CLI interface
# TODO: API KEYS


@click.group()
def cli():
    pass


# @cli.command()
# def init_post():
#     return


# TODO: WHAT WAS THE TRICK TO DIRECTLY CONVERT TO PATHLIB OBJECT?
@cli.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.option('--host', type=str, default='http://127.0.0.1:5000')
@click.option('--allow_update', type=bool, default=True)
@click.option('--publish', type=bool, default=False)
@click.option('--featured', type=bool, default=False)
def upload_post(
        path: str,
        host: str,
        allow_update: bool,
        publish: bool,
        featured: bool,
):
    # Get paths to the Markdown and metadata files
    path = pathlib.Path(path)
    md_path = path / 'post.md'
    config_path = path / 'post-meta.json'

    # Read the config file
    config = PostConfig.from_file(config_path)
    print(config)

    # Render Markdown file, getting the HTML and sourced images
    html, post_img_paths = markdown.render_file(
        md_path,
        config.slug,
    )

    # Write out html (TODO: Find a way to not require this)
    # html_path = path / 'rendered-post.html'
    # with open(html_path) as writef:
    #     writef.write(html)

    manager.upload_post(host, config, html, post_img_paths)


# Delete post
@cli.command()
@click.argument('slug', type=str)
@click.option('--host', type=str, default='http://127.0.0.1:5000')
def delete_post(slug: str, host: str):
    manager.delete_post(host, slug)


# Sync a to b
@cli.command()
def sync():
    # TODO
    return


if __name__ == '__main__':
    cli()
