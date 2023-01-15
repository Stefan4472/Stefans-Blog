import pathlib
import re
import sys

from sos_client.manager_service import ManagerService
from sos_client.postconfig import read_config_file


def migrate_markdown(post_markdown: str) -> str:
    """
    Modify the given markdown to use the `<x-image>` tag rather than the
    [figure: ...] semantics. Return the changed markdown.
    """
    # Regex used to match custom "[figure]" lines.
    # Match 1: image path
    # Match 2: optional image caption
    figure_regex = re.compile(r"\[figure: ([^,\]]+)(?:, ([^\]]+))?]")
    md_snippets = []
    last_match_index = -1

    # Iterate through '[figure: ]' instances
    for figure_match in re.finditer(figure_regex, post_markdown):
        start = figure_match.start()
        end = figure_match.end()

        # Add the Markdown between the end of the last figure match and the start of
        # this figure match (if it is non-whitespace)
        if (start != last_match_index + 1) and post_markdown[
            last_match_index + 1 : start
        ].strip():
            md_snippets.append(post_markdown[last_match_index + 1 : start])

        # Create the new "<x-image>" tag
        img_path = figure_match.group(1)
        caption = figure_match.group(2)
        md_snippets.append(_create_image_xml(img_path, caption))
        last_match_index = end

    # Add the Markdown from the last figure match to the end of the file
    if last_match_index != len(post_markdown):
        md_snippets.append(post_markdown[last_match_index + 1 :])

    return "".join(md_snippets)


def _create_image_xml(img_path: str, caption: str) -> str:
    if caption:
        return (
            f"<x-image>\n"
            f"\t<path>{img_path}</path>\n"
            f"\t<caption>{caption}</caption>\n"
            f"</x-image>\n"
        )
    else:
        return f"<x-image>\n" f"\t<path>{img_path}</path>\n" f"</x-image>\n"


if __name__ == "__main__":
    """
    Run migration for Issue #38.

    This program will go through the Markdown files of the selected posts,
    replacing their "[figure]" definitions with the new "<section type='image'>"
    tags. **This will modify all posts!**

    FILEPATH: path to a text file that contains all the post paths to migrate
    HOST: host url
    SECRET_KEY: secret used to authenticate API calls
    """
    if len(sys.argv) != 4:
        print("Usage: python run_migration.py [FILEPATH] [HOST] [SECRET_KEY]")
        sys.exit(1)

    filepath = sys.argv[1]
    host = sys.argv[2]
    key = sys.argv[3]

    service = ManagerService(host, key)
    with open(filepath) as f:
        paths = f.readlines()

    # For each path: read config, read markdown, modify and write markdown,
    # upload modified markdown
    for path_str in paths:
        post_dir = pathlib.Path(path_str.strip())
        config = read_config_file(post_dir / "post-meta.json", use_imagecropper=False)
        with open(post_dir / "post.md", encoding="utf-8", errors="strict") as f:
            markdown = f.read()
        new_markdown = migrate_markdown(markdown)
        with open(post_dir / "post.md", "w", encoding="utf-8", errors="strict") as f:
            f.write(new_markdown)
        print(f"Uploading Markdown for {config.slug}")
        service.upload_markdown(config.slug, new_markdown)
