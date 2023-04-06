import dataclasses as dc


@dc.dataclass
class PageMetadata:
    """Stores information about a page on the site, e.g. for use in HTML meta tags."""

    title: str
    description: str
    author: str
    banner_url: str
    featured_url: str
    # Control whether robots are allowed to index this page.
    allow_indexing: bool = True
