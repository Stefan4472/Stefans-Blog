# stefan-on-software-renderer

A simple wrapper around the [markdown2](https://github.com/trentm/python-markdown2) library that can render Markdown files that also include custom XML tags. I use this to render pages in [my website](https://github.com/Stefan4472/Stefans-Blog). Simply call
```
stefan_on_software_renderer.render_string(post_text: str)
```

to render the provided text. You can add a figure to your markdown using the custom `x-image` tag:
```
<x-image>
  <path>colorwheel.png</path>
  <caption>The RGB color wheel ([source](https://cdn.sparkfun.com/r/600-600/assets/learn_tutorials/7/1/0/TertiaryColorWheel_Chart.png))</caption>
  <alt>Image of the RGB color wheel</alt>
</x-image>
```

You can add a code block with [pygments](https://pygments.org/) syntax highlighting using the custom `<x-code>` tag:
```
# See the pygments languages documentation for a list of possible "language" arguments (https://pygments.org/languages/). Leave blank for no styling
<x-code language="python">
if __name__ == '__main__':
    print('Hello world')
</x-code>
```

The utility function `find_images()` can be used to get all the `paths` from the `x-image` tags in the string. `is_markdown_valid()` can be used to test whether a given text can be correctly rendered.
