import flask
import re
import randomcolor


def get_uploaded_file(request: flask.Request) -> (bytes, str):
    """
    Get the file uploaded with the given Request.

    Returns a tuple containing the raw data and the uploaded filename.
    Throws ValueError if `request` does not have exactly one file uploaded.
    """
    if len(request.files) == 0:
        raise ValueError('No file uploaded')
    elif len(request.files) > 1:
        raise ValueError('More than one file uploaded')
    file = list(request.files.values())[0]
    data = file.read()
    file.close()
    return data, file.filename


def generate_slug(string: str) -> str:
    """
    Generates a slug from the given string.

    Slugs are used to create readable urls.
    """
    string = string.replace(' ', '-').lower()
    # Remove any non letters, numbers, and non-dashes
    return re.sub(r'[^a-zA-Z0-9\-\+]+', '', string)


def generate_random_color() -> str:
    """Generates a random color and returns it as a hex string."""
    return randomcolor.RandomColor().generate(luminosity='light', count=1)[0]
