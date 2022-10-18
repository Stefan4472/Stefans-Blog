import dataclasses as dc
from datetime import datetime
from typing import Dict


@dc.dataclass
class UserContract:
    id: int
    name: str

    def make_json(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
        }


@dc.dataclass
class FileContract:
    id: str
    upload_name: str
    upload_date: datetime
    uploaded_by: UserContract
    filetype: str
    filename: str
    url: str
    size: int
    hash: str

    def make_json(self) -> Dict:
        return {
            'id': self.id,
            'upload_name': self.upload_name,
            'upload_date': str(self.upload_date),
            'uploaded_by': self.uploaded_by.make_json(),
            'filetype': self.filetype.value,
            'filename': self.filename,
            'url': self.url,
            'size': self.size,
            'hash': self.hash,
        }
