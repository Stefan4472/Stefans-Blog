import werkzeug
import hashlib
import io
import os
import uuid
import dataclasses as dc
from flask import current_app
from PIL import Image, UnidentifiedImageError
from datetime import datetime
from flaskr import db
from flaskr.models.file import File, FileType
from flaskr.models.user import User
import flaskr.contracts.constants as constants


class FileAlreadyExists(ValueError):
    """
    Exception thrown when a file with the same contents already
    exists on the server.
    """
    def __init__(self, duplicate: File):
        self.duplicate = duplicate


class InvalidExtension(ValueError):
    """
    Exception thrown when a file has an extension that is not
    supported by the server.
    """
    def __init__(self, extension: str):
        self.extension = extension


class InvalidFile(ValueError):
    pass


ALLOWED_EXTENSIONS = [
    '.jpg',
    '.png',
    '.gif',
    '.txt',
    '.pdf',
]


def file_exists(file_id: str) -> bool:
    """Return whether the file with given ID is stored on the system."""
    return bool(File.query.filter_by(id=file_id).first())


def store_file(file: werkzeug.datastructures.FileStorage, created_by: User) -> File:
    file_name = werkzeug.utils.secure_filename(file.filename)
    current_app.logger.debug(f'Storing file with filename {file_name}')

    # Validate file extension
    original_extension = get_extension(file_name)
    if original_extension not in ALLOWED_EXTENSIONS:
        raise InvalidExtension(original_extension)

    # TODO: I don't know whether it's a good idea to directly modify the file.
    #  It would be good to store the original, but serve a compressed or CDN version
    # Process the file
    contents = io.BytesIO(file.read())
    processed = _process_file(contents, original_extension)

    # Check if a file with the same hash already exists
    file_hash = hashlib.md5(processed.contents.getbuffer()).hexdigest()
    query = File.query.filter_by(hash=file_hash)
    if query.first():
        current_app.logger.debug(f'File is a duplicate of {query.first().id}')
        raise FileAlreadyExists(query.first())

    file_id = uuid.uuid4().hex
    file = File(
        id=file_id,
        upload_name=file_name,
        upload_date=datetime.now(),
        uploaded_by=created_by,
        filetype=get_file_type(processed.extension),
        filename=file_id + processed.extension,
        hash=file_hash,
    )

    # Save to file system
    with open(file.get_path(), 'wb') as out:
        out.write(processed.contents.getbuffer())
    file.size = os.path.getsize(file.get_path())

    db.session.add(file)
    db.session.commit()
    current_app.logger.debug(f'File stored successfully with ID={file.id}')
    return file


def delete_file(file: File):
    """Delete the given file from the file system and the database."""
    # TODO: fail if references exist
    try:
        # Delete from filesystem
        file.get_path().unlink()
    except FileNotFoundError:
        # Doesn't exist anymore... strange but doesn't matter at this point
        current_app.logger.warning(f'Attempted to delete {file.get_path()}, which doesn\'t exist')

    db.session.delete(file)
    db.session.commit()
    current_app.logger.debug(f'Deleted file with id={file.id}')


def get_extension(filename: str) -> str:
    if '.' not in filename:
        return ''
    return filename[filename.rindex('.'):].lower()


def get_file_type(extension: str) -> FileType:
    if extension in ('.jpg', '.png', '.gif'):
        return FileType.Image
    elif extension in ('.txt', '.pdf'):
        return FileType.Document
    else:
        raise ValueError(f'Unsupported extension {extension}')


@dc.dataclass
class ProcessedFile:
    contents: io.BytesIO
    extension: str


def _process_file(file: io.BytesIO, extension: str) -> ProcessedFile:
    if extension in ('.jpg', '.png'):
        # Convert still images to JPG and limit to MAX_IMG_SIZE
        try:
            image: Image = Image.open(file)
        except UnidentifiedImageError:
            raise InvalidFile('Cannot read image')
        # Bound to MAX_IMG_SIZE
        if image.width > constants.MAX_IMG_WIDTH or image.height > constants.MAX_IMG_HEIGHT:
            image.thumbnail((constants.MAX_IMG_WIDTH, constants.MAX_IMG_HEIGHT), Image.ANTIALIAS)
        # Convert to RGB (for saving to JPG)
        image = image.convert('RGB')
        # Write out to buffer
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        return ProcessedFile(image_bytes, '.jpg')
    else:
        # Do nothing
        return ProcessedFile(file, extension)
