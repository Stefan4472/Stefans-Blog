from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

from ..models.file_filetype import FileFiletype

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="File")


@attr.s(auto_attribs=True)
class File:
    """A file stored on the webserver

    Attributes:
        id (str): UUID used to identify this file. Example: 1f536f1b-cb44-41e2-be18-c89140d0f02c.
        upload_name (str): Original filename used when uploading this file. Example: java_screenshot.jpg.
        upload_date (str): Timestamp at which this file was uploaded. Example: 2022-09-01 17:22:12+00:00.
        uploaded_by (User): A registered user
        filetype (FileFiletype): General type of the file (determined by server during upload). Example: IMAGE.
        filename (str): Filename, as stored on the webserver. Example: 1f536f1b-cb44-41e2-be18-c89140d0f02c.jpg.
        url (str): URL that this file can be accessed under on the public website. Example:
            https://www.stefanonsoftware.com/static/1f536f1b-cb44-41e2-be18-c89140d0f02c.jpg.
        size (int): Size of the file, in bytes. Example: 330060.
        hash_ (str): MD5 hash of the file contents. Example: d7e1fcfe6aae23c19e69511c48e37a73.
    """

    id: str
    upload_name: str
    upload_date: str
    uploaded_by: "User"
    filetype: FileFiletype
    filename: str
    url: str
    size: int
    hash_: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        upload_name = self.upload_name
        upload_date = self.upload_date
        uploaded_by = self.uploaded_by.to_dict()

        filetype = self.filetype.value

        filename = self.filename
        url = self.url
        size = self.size
        hash_ = self.hash_

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "upload_name": upload_name,
                "upload_date": upload_date,
                "uploaded_by": uploaded_by,
                "filetype": filetype,
                "filename": filename,
                "url": url,
                "size": size,
                "hash": hash_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.user import User

        d = src_dict.copy()
        id = d.pop("id")

        upload_name = d.pop("upload_name")

        upload_date = d.pop("upload_date")

        uploaded_by = User.from_dict(d.pop("uploaded_by"))

        filetype = FileFiletype(d.pop("filetype"))

        filename = d.pop("filename")

        url = d.pop("url")

        size = d.pop("size")

        hash_ = d.pop("hash")

        file = cls(
            id=id,
            upload_name=upload_name,
            upload_date=upload_date,
            uploaded_by=uploaded_by,
            filetype=filetype,
            filename=filename,
            url=url,
            size=size,
            hash_=hash_,
        )

        file.additional_properties = d
        return file

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
