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
    actual = md2.render_string(example_markdown)
    assert actual.strip() == example_html.strip()


def test_find_images(example_markdown):
    """Test that `find_images()` works as expected on the example Markdown."""
    actual = md2.find_images(example_markdown)
    expected = ['vintage-film-reel.jpg', 'example-draw-square.jpg', 'example-moving-square.gif', 'example-changing-square.gif']
    assert actual == expected


def test_render_code():
    """Test that <> strings are correctly rendered."""
    str = '''
<x-code language="c++">
unordered_map<ItemType, list<InvCoordinate>> mainInvMappings;
unordered_map<ItemType, list<InvCoordinate>> hotbarMappings;
</x-code>'''
    expected = '''<div>{% raw %}<div class="highlight" style="background: #f8f8f8"><pre style="line-height: 125%;"><span></span>unordered_map<span style="color: #666666">&lt;</span>ItemType,<span style="color: #bbbbbb"> </span>list<span style="color: #666666">&lt;</span>InvCoordinate<span style="color: #666666">&gt;&gt;</span><span style="color: #bbbbbb"> </span>mainInvMappings;<span style="color: #bbbbbb"></span>
unordered_map<span style="color: #666666">&lt;</span>ItemType,<span style="color: #bbbbbb"> </span>list<span style="color: #666666">&lt;</span>InvCoordinate<span style="color: #666666">&gt;&gt;</span><span style="color: #bbbbbb"> </span>hotbarMappings;<span style="color: #bbbbbb"></span>
</pre></div>{% endraw %}</div>'''
    assert md2.render_string(str).strip() == expected