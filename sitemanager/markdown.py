import typing
import re


def find_images(post_markdown: str) -> typing.List[str]:
    """
    Read the provided Markdown string and return a list of found image
    paths as typed in the Markdown (these will likely be paths relative
    to the original Markdown file's location).
    """
    # Regex used to match custom "[figure]" lines.
    # Match 1: image path
    # Match 2: optional image caption
    figure_regex = re.compile(r'\[figure: ([^,\]]+)(?:, ([^\]]+))?]')
    images = []

    # Iterate through '[figure: ]' matches
    for figure_match in re.finditer(figure_regex, post_markdown):
        # Append file name
        images.append(figure_match.group(1))
    return images
