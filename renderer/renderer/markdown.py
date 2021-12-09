import pathlib
import typing
import markdown2
import bs4
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


def get_static_url(rel_path_from_static: str) -> str:
    """
    Create a `url_for()` template function with a relative path from
    the `static` folder.
    """
    # TODO: FIND A WAY TO REFACTOR THIS OUT. Allow user to provide their own formatting function, or some other mechanism for building URLs
    return '{{{{ url_for(\'static\', filename=\'{}\') }}}}'.format(
        rel_path_from_static
    )


def render_string(
        post_markdown: str,
        post_slug: str,
) -> str:
    """
    Read the provided Markdown text and render to HTML, including custom tags.

    Returns the HTML as a string
    """
    # Collect rendered segments in a list, which will be joined at the end.
    # This is far more efficient than repeated concatenation.
    segments: typing.List[str] = []
    soup = bs4.BeautifulSoup(post_markdown, features='html.parser')
    # Loop over top-level tags
    for tag in soup.contents:
        # Ignore blank lines
        if str(tag).isspace():
            continue
        # No tag: render text as Markdown by default
        elif tag.name == None:
            segments.append(str(bs4.BeautifulSoup(markdown2.markdown(str(tag).strip()), features='html.parser')).strip())
        # Found an `<x-image>` tag
        elif tag.name == 'x-image':
            segments.append(str(_render_image(tag, post_slug)).strip())
        # Found an `<x-code>` tag
        elif tag.name == 'x-code':
            segments.append(str(_render_code(tag)).strip() + '\n')
    return '\n'.join(segments)


def _render_image(
        image_elem: bs4.element.Tag,
        post_slug: str,
) -> bs4.BeautifulSoup:
    """
    Render custom <x-image> tag into a BeautifulSoup object.

    `image_elem`: the tag as it exists in the current BS4 tree
    `post_slug`: the post's slug, used to build the image URL
    """
    path_elems = image_elem.findChildren('path', recursive=False)
    caption_elems = image_elem.findChildren('caption', recursive=False)
    alt_elems = image_elem.findChildren('alt', recursive=False)

    if len(path_elems) != 1:
        raise ValueError('"x-image" tag does not have exactly one "path" specified')
    if len(caption_elems) == 2:
        raise ValueError('"x-image" tag has more than one "caption" specified')
    if len(alt_elems) == 2:
        raise ValueError('"x-image" tag has more than one "alt" specified')

    path = path_elems[0].contents[0]
    caption = caption_elems[0].contents[0] if caption_elems else None
    alt = alt_elems[0].contents[0] if alt_elems else ''

    # Form image URL using image filename and post slug
    img_url = get_static_url(post_slug + '/' + pathlib.Path(path).name)
    # img_url = flask.url_for('static', filename=post_slug + '/' + pathlib.Path(path).name)

    # Render custom <figure> HTML
    figure_html = _create_figure_html(img_url, caption, alt)
    return bs4.BeautifulSoup(figure_html, features='html.parser')


def _create_figure_html(url: str, caption: str = None, alt: str = '') -> str:
    """Given parameters, return an HTML string of a `figure` element."""
    if caption:
        # This is a dumb workaround to render the caption but remove the leading "<p>"
        caption_html = markdown2.markdown(caption).replace(r'<p>', '').replace(r'<\p>', '').strip()
        return (
            f'<figure class="figure text-center">'
            f'    <img src="{url}" class="figure-img img-fluid img-thumbnail rounded" alt="{alt}">'
            f'    <figcaption class="figure-caption">{caption_html}</figcaption>'
            f'</figure>'
        )
    else:
        return (
            f'<figure class="figure text-center">'
            f'    <img src="{url}" class="figure-img img-fluid img-thumbnail rounded" alt="{alt}">'
            f'</figure>'
        )


def _render_code(code_elem: bs4.element.Tag) -> bs4.BeautifulSoup:
    language = code_elem['language'] if code_elem.has_attr('language') else None
    contents = code_elem.contents[0]
    try:
        # Use `TextLexer` as default if no language specified
        lexer = get_lexer_by_name(language if language else 'text')
    except pygments.util.ClassNotFound:
        raise ValueError(f'Invalid "language" parameter in <x-code> element {language}')
    # TODO: COULD PROVIDE A GLOBAL SETTING FOR THE 'STYLE' TO USE (see https://pygments.org/styles/)
    # https://pygments.org/docs/formatters/#HtmlFormatter
    formatter = HtmlFormatter(noclasses=True)
    code_html = pygments.highlight(contents.strip(), lexer, formatter)
    return bs4.BeautifulSoup(code_html, features='html.parser')


def find_images(post_markdown: str) -> typing.List[str]:
    """
    Read the provided Markdown string and return a list of found image
    paths as given in custom "<figure>" tags. These will likely be paths
    relative to the original Markdown file's location).
    """
    soup = bs4.BeautifulSoup(post_markdown, features='html.parser')
    paths = []
    for image_elem in soup.find_all('x-image'):
        paths.append(image_elem.findChildren('path', recursive=False)[0].contents[0])
    return paths
