import pytest
import pathlib
import renderer.markdown as md2
"""
A couple very simple tests.

Use `example.md` as input and `example.html` as the expected output.
"""


# Markdown example file
MD_PATH = pathlib.Path(__file__).parent / 'example.md'
# Expected HTML output
HTML_PATH = pathlib.Path(__file__).parent / 'example.html'


@pytest.fixture
def example_markdown():
    """Load and return the text from the example markdown file."""
    with open(MD_PATH, encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def example_html():
    """Load and return the text from the example HTML file."""
    with open(HTML_PATH, encoding='utf-8') as f:
        return f.read()


def test_render(example_markdown, example_html):
    """Test that `render_string()` of the example Markdown yields the example HTML"""
    actual = md2.render_string(example_markdown, 'gamedev-animation')
    assert actual.strip() == example_html.strip()


def test_find_images(example_markdown):
    """Test that `find_images()` works as expected on the example Markdown."""
    actual = md2.find_images(example_markdown)
    expected = ['vintage-film-reel.jpg', 'example-draw-square.jpg', 'example-moving-square.gif', 'example-changing-square.gif']
    assert actual == expected
