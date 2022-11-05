import click
import sys
from typing import Optional, List
from pathlib import Path
from datetime import date
from imagecropper import cropper
from sos_client.post_meta import PostMeta
from sos_client import constants


@click.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path))
def prepare_post(path: Path):
    """
    Prepare a post for upload.

    PATH: path to the directory where the `post.md` to prepare lives.
    """
    md_path = path / 'post.md'
    if not md_path.exists():
        click.echo(f'Could not find a post.md in {path.absolute()}', err=True)
        sys.exit(1)
    if not md_path.is_file():
        click.echo(f'Found a post.md in {path.absolute()} but it is not a file', err=True)
        sys.exit(1)

    post_meta = PostMeta()
    meta_path = path / 'post-meta.json'
    if meta_path.exists():
        click.echo(f'Found meta file {meta_path.absolute()}')
        # TODO: what exceptions can happen?
        post_meta = PostMeta.parse_from_file(meta_path)
        click.echo('Read metadata from existing post-meta.json')

    # TODO: validate slugs
    post_meta.slug = decide_slug(post_meta.slug)
    post_meta.title = decide_title(post_meta.title)
    post_meta.byline = decide_byline(post_meta.byline)
    post_meta.date = decide_date(post_meta.date)
    post_meta.tags = decide_tags(post_meta.tags)
    post_meta.image = decide_featured_image(path, post_meta.image)
    post_meta.banner = decide_banner_image(path, post_meta.banner)
    post_meta.thumbnail = decide_thumbnail_image(path, post_meta.thumbnail)
    print(post_meta)

    # Write out the meta
    post_meta.write_to_file(meta_path)
    click.echo(f'Wrote metadata to {meta_path.absolute()}')

def decide_slug(default: Optional[str]) -> str:
    return click.prompt('Enter slug:', default=default if default else '', type=str)


def decide_title(default: Optional[str]) -> str:
    return click.prompt('Enter title:', default=default if default else '', type=str)


def decide_byline(default: Optional[str]) -> str:
    return click.prompt('Enter byline:', default=default if default else '', type=str)


def decide_date(default: Optional[date]) -> date:
    return default if default else date.today()


def decide_tags(default: Optional[List[str]]) -> List[str]:
    if default and _confirm_choice(f'Current tags are: {",".join(default)}'):
        return default
    tag_str = click.prompt('Enter comma-separated tags', type=str)
    tags = [tag.strip() for tag in tag_str.split(',')]


def decide_featured_image(post_dir: Path, default: Optional[Path]) -> Path:
    if default and _confirm_choice(f'Current featured image is: {default}'):
        return default
    image_path = cropper.choose_image(post_dir)
    write_path = post_dir / 'featured.jpg'
    cropper.run_image_cropper(
        image_path,
        *constants.FEATURED_IMG_SIZE,
        write_path,
    )
    return write_path


def decide_banner_image(post_dir: Path, default: Optional[Path]) -> Path:
    if default and _confirm_choice(f'Current banner is: {default}'):
        return default
    image_path = cropper.choose_image(post_dir)
    write_path = post_dir / 'banner.jpg'
    cropper.run_image_cropper(
        image_path,
        *constants.BANNER_SIZE,
        write_path,
    )
    return write_path


def decide_thumbnail_image(post_dir: Path, default: Optional[Path]) -> Path:
    if default and _confirm_choice(f'Current thumbnail is: {default}'):
        return default
    image_path = cropper.choose_image(post_dir)
    write_path = post_dir / 'thumbnail.jpg'
    cropper.run_image_cropper(
        image_path,
        *constants.THUMBNAIL_SIZE,
        write_path,
    )
    return write_path


def _confirm_choice(prompt: str):
    """
    Runs a confirmation (y/n) dialog in a loop.
    Click has a confirmation prompt but it's annoying to use.
    """
    confirm_res = ''
    while confirm_res not in ('y', 'n'):
        confirm_res = click.prompt(f'{prompt}. Confirm? (y/n)')
    return confirm_res == 'y'


if __name__ == '__main__':
    prepare_post()
