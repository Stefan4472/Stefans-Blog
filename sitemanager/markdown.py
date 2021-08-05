import pathlib
import typing
import re
import markdown2
import util


def render_file(
        filepath: pathlib.Path,
        post_slug: str,
) -> typing.Tuple[str, typing.List[pathlib.Path]]:
    """
    Read the provided Markdown file and render to HTML.
    Images will be redered as Bootstrap figures.

    Returns the HTML as a string, and a list of all image sources
    found in the document.

    TODO: EXPLAIN HOW TO ADD A CAPTION
    TODO: THIS WHOLE FUNCTION SHOULD BE CLEANED UP
    -> create "Markdown Processer" class
    """
    # Regex used to match custom "[figure]" lines.
    # Match 1: image path
    # Match 2: optional image caption
    figure_regex = re.compile(r'\[figure: ([^,\]]+)(?:, ([^\]]+))?]')
    html_snippets = []
    images = []
    last_match_index = -1

    try:
        with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
            post_markdown = f.read()
    except IOError:
        msg = 'Could not read the post file ("{}")'.format(filepath)
        raise ValueError(msg)

    # Iterate through '[figure: ]' instances, which must be handled specially.
    # Everything else can be rendered using the 'markdown' library.
    for figure_match in re.finditer(figure_regex, post_markdown):
        start = figure_match.start()
        end = figure_match.end()

        # Render the Markdown between the end of the last figure match and the start of
        # this figure match (if it is non-whitespace)
        if (start != last_match_index + 1) and post_markdown[last_match_index + 1: start].strip():
            rendered_html = markdown2.markdown(post_markdown[last_match_index + 1: start], extras=['fenced-code-blocks'])
            html_snippets.append(rendered_html)

        # Render the figure
        img_path = figure_match.group(1)
        img_caption = figure_match.group(2)

        # TODO: CLEAN UP
        img_url = util.get_static_url(post_slug + '/' + pathlib.Path(img_path).name)

        # Render with caption
        # TODO: HANDLE alt, and make this string a constant (?)
        if img_caption:
            rendered_html = \
                '''
                <figure class="figure text-center">
                    <img src="{}" class="figure-img img-fluid img-thumbnail rounded" alt="">
                    <figcaption class="figure-caption">{}</figcaption>
                </figure>

                '''.format(img_url, img_caption)
        # Render without caption
        else:
            rendered_html = \
                '''
                <figure class="figure text-center">
                    <img src="{}" class="figure-img img-fluid img-thumbnail rounded" alt="">
                </figure>

                '''.format(img_url)

        images.append(pathlib.Path(img_path))
        html_snippets.append(rendered_html)
        last_match_index = end

    # Render the Markdown from the last figure match to the end of the file
    if last_match_index != len(post_markdown):
        rendered_html = markdown2.markdown(post_markdown[last_match_index + 1:], extras=['fenced-code-blocks'])
        html_snippets.append(rendered_html)
        # print (rendered_html)

    return ''.join(html_snippets), images
