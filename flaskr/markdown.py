import flask
import pathlib
import markdown2
import bs4


def render_string(
        post_markdown: str,
        post_slug: str,
) -> str:
    """
    Read the provided Markdown file and render to HTML.
    Images will be rendered as Bootstrap figures.
    Returns the HTML as a string
    TODO: EXPLAIN HOW CUSTOM FIGURES ARE RENDERED
    """
    # Render to HTML
    html = markdown2.markdown(post_markdown, custom_tags=['x-image'])
    # Read in the rendered HTML
    soup = bs4.BeautifulSoup(html, features='html.parser')

    # Process images
    for image_elem in soup.find_all('x-image'):
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
        img_url = flask.url_for('static', filename=post_slug + '/' + pathlib.Path(path).name)

        # Render custom <figure> HTML and replace the current `section`
        # with the new node
        figure_html = _render_figure(img_url, caption, alt)
        image_elem.replace_with(bs4.BeautifulSoup(figure_html, features='html.parser'))
    # Return potentially-modified HTML
    return str(soup)


def _render_figure(url: str, caption: str = None, alt: str = '') -> str:
    """Given parameters, return an HTML string of a `figure` element."""
    if caption:
        # This is a dumb workaround to render the caption but remove the leading "<p>"
        caption_html = markdown2.markdown(caption).replace('<p>', '').replace('<\p>', '')
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
