"""
Functions for rendering and handling post text, which consists of Markdown
and custom XML tags.

TODO: needs significant cleanup and clear documentation.
"""
import re
import typing

import bs4
import markdown2
import pygments
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

IMAGE_TAG = "x-image"
CODE_TAG = "x-code"
CUSTOM_TAGS = [IMAGE_TAG, CODE_TAG]

# Note: this will not support tags such as "<x-code/>". Each tag needs an open and a close.
MATCH_TAG_OPEN = re.compile(f'<({"|".join(CUSTOM_TAGS)})[^>]*>')
MATCH_TAG_CLOSE = re.compile(f'</({"|".join(CUSTOM_TAGS)})>')


def render_string(post_text: str) -> str:
    """
    Render the provided text into HTML. This will also render custom tags.

    Rendering proceeds in two stages. First, the custom tags are found and
    individually rendered into HTML. The resulting "preprocessed" text is
    then run through the Markdown-to-HTML renderer, which will ignore
    the custom generated HTML.

    Returns the rendered HTML as a string.
    """
    prev_index = 0
    segments: typing.List[str] = []
    # Note: unfortunately we can't use BeautifulSoup here because it can cause
    # problems with x-code elements, which may contain "<" and ">".
    # We need to maintain access to the raw strings.
    for match_open in re.finditer(MATCH_TAG_OPEN, post_text):
        tag_name = match_open.group(1)
        close_start, close_end = _find_closing_tag(
            tag_name, post_text, match_open.end()
        )
        raw_segment = post_text[match_open.start() : close_end]

        # Run BeautifulSoup *on the segment* for parsing the XML
        element = bs4.BeautifulSoup(raw_segment, features="html.parser").contents[0]
        if tag_name == IMAGE_TAG:
            rendered_segment = _render_image(element) + "\n"
        elif tag_name == CODE_TAG:
            raw_contents = post_text[match_open.end() : close_start]
            rendered_segment = _render_code(element, raw_contents)
        else:
            raise ValueError(
                f'Unsupported tag "{tag_name}". This is a programmer error'
            )

        segments.append(post_text[prev_index : match_open.start()])
        segments.append(rendered_segment)
        prev_index = close_end

    segments.append(post_text[prev_index:])
    # Filter out empty strings
    processed = "\n".join([s for s in segments if s and s != "\n"])

    # Run the Markdown renderer over the processed result
    return markdown2.markdown(processed)


def _find_closing_tag(tag_name: str, text: str, pos: int) -> typing.Tuple[int, int]:
    """
    Find the closing tag for `tag_name` in `text` starting at `pos`.

    Returns a tuple containing (start, end) of the closing tag, indexed in `text`.
    """
    # Search for the next closing tag after the current open
    match_close = re.search(MATCH_TAG_CLOSE, text[pos:])
    if not match_close or match_close.group(1) != tag_name:
        raise ValueError(f"An {tag_name} tag is not closed")
    return (pos + match_close.start(), pos + match_close.end())


def _render_image(image_elem: bs4.element.Tag) -> str:
    """
    Render custom <x-image> tag into an HTML string.

    `image_elem`: the tag as it exists in the current BS4 tree
    """
    path_elems = image_elem.findChildren("path", recursive=False)
    caption_elems = image_elem.findChildren("caption", recursive=False)
    alt_elems = image_elem.findChildren("alt", recursive=False)

    if len(path_elems) != 1:
        raise ValueError('"x-image" tag does not have exactly one "path" specified')
    if len(caption_elems) == 2:
        raise ValueError('"x-image" tag has more than one "caption" specified')
    if len(alt_elems) == 2:
        raise ValueError('"x-image" tag has more than one "alt" specified')

    path = path_elems[0].contents[0]
    caption = caption_elems[0].contents[0] if caption_elems else None
    alt = alt_elems[0].contents[0] if alt_elems else ""

    # Render custom <figure> HTML
    return _create_figure_html(path, caption, alt)


def _create_figure_html(url: str, caption: str = None, alt: str = "") -> str:
    """Given parameters, return an HTML string of a `figure` element."""
    if caption:
        # This is a dumb workaround to render the caption but remove the leading "<p>"
        # TODO: ALL WE NEED IS SIMPLE LINK-HANDLING. THIS COULD PROBABLY BE DONE WITH REGEX
        caption_html = (
            markdown2.markdown(caption).replace(r"<p>", "").replace(r"<\p>", "").strip()
        )
        return (
            f'<figure class="figure text-center">'
            f'    <img src="{url}" class="figure-img img-fluid img-thumbnail rounded" alt="{alt}">'
            f'    <figcaption class="figure-caption">{caption_html}</figcaption>'
            f"</figure>"
        )
    else:
        return (
            f'<figure class="figure text-center">'
            f'    <img src="{url}" class="figure-img img-fluid img-thumbnail rounded" alt="{alt}">'
            f"</figure>"
        )


def _render_code(code_elem: bs4.element.Tag, raw_contents: str) -> str:
    """Render custom <x-code> element into an HTML string."""
    language = code_elem["language"] if code_elem.has_attr("language") else None
    try:
        # Use `TextLexer` as default if no language specified
        lexer = get_lexer_by_name(language if language else "text")
    except pygments.util.ClassNotFound:
        raise ValueError(f'Invalid "language" parameter in <x-code> element {language}')
    # TODO: COULD PROVIDE A GLOBAL SETTING FOR THE 'STYLE' TO USE (see https://pygments.org/styles/)
    # https://pygments.org/docs/formatters/#HtmlFormatter
    formatter = HtmlFormatter(noclasses=True)
    # Render pygments within a Jinja "raw" block to avoid inadvertent template evaluation
    return (
        r"<div>{% raw %}"
        + pygments.highlight(raw_contents.strip(), lexer, formatter).strip()
        + r"{% endraw %}</div>"
    )


def find_images(post_markdown: str) -> typing.List[str]:
    """
    Read the provided Markdown string and return a list of found image
    paths as given in custom "<figure>" tags.

    These will likely be paths relative to the original Markdown file's location).
    """
    soup = bs4.BeautifulSoup(post_markdown, features="html.parser")
    paths = []
    for image_elem in soup.find_all("x-image"):
        paths.append(
            image_elem.findChildren("path", recursive=False)[0]
            .contents[0]
            .replace('"', "")
        )
    return paths


def is_markdown_valid(markdown: str) -> bool:
    # Render HTML to check for errors
    try:
        render_string(markdown)
        return True
    except Exception:
        return False
