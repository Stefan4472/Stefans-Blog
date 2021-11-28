import typing
import re
import bs4


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
