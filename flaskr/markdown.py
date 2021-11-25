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
    html = markdown2.markdown(post_markdown)
    # Read in the rendered HTML
    soup = bs4.BeautifulSoup(html, features='html.parser')
    # Process images: for each `section` element with `type=='image'`, create
    # a `<figure>`.
    for section in soup.find_all('section'):
        if section.has_attr('type') and section['type'] == 'image':
            if not section.has_attr('path'):
                raise ValueError('Custom "section" image tag missing required attribute "path"')

            path = section['path']
            caption = section['caption'] if section.has_attr('caption') else None
            alt = section['alt'] if section.has_attr('alt') else None

            # Form image URL using image filename and post slug
            img_url = flask.url_for('static', filename=post_slug + '/' + pathlib.Path(path).name)

            # Render custom <figure> HTML and replace the current `section`
            # with the new node
            figure_html = _render_figure(img_url, caption, alt)
            section.replace_with(bs4.BeautifulSoup(figure_html))
    # Return potentially-modified BS4 object
    return str(soup)


def _render_figure(url: str, caption: str = None, alt: str = None) -> str:
    """Given parameters, return an HTML string of a `figure` element."""
    # This is a dumb workaround to render the caption but remove the leading "<p>"
    caption_html = markdown2.markdown(caption).replace('<p>', '').replace('<\p>', '')
    if caption:
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
