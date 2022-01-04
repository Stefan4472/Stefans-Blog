import flask


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
