import werkzeug
import hashlib
import io
import uuid
import dataclasses as dc
from flask import current_app
from PIL import Image, UnidentifiedImageError
from datetime import datetime
from pathlib import Path
from flaskr import db
from flaskr.models.file import File, FileType
from flaskr.models.user import User
import flaskr.api.constants as constants


class FileAlreadyExists(ValueError):
    """
    Exception thrown when a file with the same contents already
    exists on the server.
    """
    def __init__(self, duplicate: File):
        self.duplicate = duplicate


class InvalidExtension(ValueError):
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


def store_file(file: werkzeug.datastructures.FileStorage, created_by: User) -> File:
    file_name = werkzeug.utils.secure_filename(file.filename)
    current_app.logger.debug(f'Storing file with filename {file_name}')

    # Validate file extension
    original_extension = get_extension(file_name)
    print(original_extension)
    if original_extension not in ALLOWED_EXTENSIONS:
        raise InvalidExtension(original_extension)

    # Check if a file with the same hash already exists
    contents = io.BytesIO(file.read())
    file_hash = hashlib.md5(contents.getbuffer()).hexdigest()
    query = File.query.filter_by(hash=file_hash)
    if query.first():
        current_app.logger.debug(f'File is a duplicate of {query.first().id}')
        raise FileAlreadyExists(query.first())

    # Process the file
    # TODO: honestly, I don't think it's a good idea to directly modify the file. Would be good to keep the original, but serve a compressed version
    processed = _process_file(contents, original_extension)

    # Generate random UUID
    file_id = uuid.uuid4().hex
    # Create file. Store ORIGINAL hash -> TODO: I don't like that. Shouldn't store original hash, it makes no sense. First, process, then check the hash (I guess)
    file = File(
        id=file_id,
        upload_name=file_name,
        upload_date=datetime.now(),
        uploaded_by=created_by,
        filetype=get_file_type(processed.extension),
        filename=file_id + processed.extension,
        size=file.content_length,  # TODO: this is the ORIGINAL SIZE. And it's wrong
        hash=file_hash,
    )

    # Save to file system
    with open(file.get_path(), 'wb') as out:
        out.write(processed.contents.getbuffer())

    db.session.add(file)
    db.session.commit()
    current_app.logger.debug(f'File stored successfully with ID={file.id}')
    return file


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
            image.thumbnail(constants.MAX_IMG_SIZE, Image.ANTIALIAS)
        # Convert to RGB (for saving to JPG)
        image = image.convert('RGB')
        # Write out to buffer
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPG')
        return ProcessedFile(image_bytes, '.jpg')
    else:
        # Do nothing
        return ProcessedFile(file, extension)
