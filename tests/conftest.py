import pytest

from google_drive_sync.drive_manager import DriveManager


class _ExecWrapper:
    def __init__(self, payload):
        self._payload = payload

    def execute(self):
        return self._payload


# ---- Fake Drive API ----
class FakeDriveFiles:
    def __init__(self):
        self._last_query = None

    def list(self, q=None, fields=None, pageToken=None, pageSize=None):
        self._last_query = q or ""
        # Decide response based on query (folders vs files)
        if "mimeType='application/vnd.google-apps.folder'" in self._last_query:
            payload = {
                "files": [
                    {"id": "folder1", "name": "Folder One", "parents": ["root"]},
                    {"id": "folder2", "name": "Folder Two", "parents": ["root"]},
                    {"id": "folder3", "name": "Folder Three", "parents": ["root"]},
                ]
            }
        else:
            # Non-folder files (media and non-media)
            payload = {
                "files": [
                    {
                        "id": "file1",
                        "name": "photo1.jpg",
                        "mimeType": "image/jpeg",
                        "parents": ["root"],
                    },
                    {
                        "id": "file2",
                        "name": "video1.mp4",
                        "mimeType": "video/mp4",
                        "parents": ["root"],
                    },
                    {
                        "id": "file3",
                        "name": "notes.txt",
                        "mimeType": "text/plain",
                        "parents": ["root"],
                    },
                ]
            }
        return _ExecWrapper(payload)


class FakeDriveService:
    def files(self):
        return FakeDriveFiles()


# ---- Fake Photos API ----
class FakeMediaItems:
    def __init__(self):
        self._last_body = None

    def search(self, body=None):
        self._last_body = body or {}
        return _ExecWrapper(
            {
                "mediaItems": [
                    {
                        "id": "m1",
                        "filename": "IMG_0001.JPG",
                        "mimeType": "image/jpeg",
                        "baseUrl": "https://example.com/m1",
                        "mediaMetadata": {
                            "creationTime": "2024-01-01T12:00:00Z",
                            "width": "4032",
                            "height": "3024",
                            "photo": {
                                "cameraMake": "Apple",
                                "cameraModel": "iPhone",
                            },
                        },
                    },
                    {
                        "id": "m2",
                        "filename": "VID_0001.MP4",
                        "mimeType": "video/mp4",
                        "baseUrl": "https://example.com/m2",
                        "mediaMetadata": {
                            "creationTime": "2024-01-02T10:00:00Z",
                            "width": "1920",
                            "height": "1080",
                            "video": {
                                "fps": 30.0,
                                "status": "READY",
                            },
                        },
                    },
                ]
            }
        )

    # Provide list as well for completeness (not used by these tests)
    def list(self, body=None):
        return self.search(body=body)


class FakePhotosService:
    def mediaItems(self):
        return FakeMediaItems()


# ---- Fake Auth Manager exposed via fixture ----
class FakeAuthManager:
    def __init__(self):
        self._drive = FakeDriveService()
        self._photos = FakePhotosService()

    def authenticate(self) -> bool:
        return True

    def get_drive_service(self):
        return self._drive

    def get_photos_service(self):
        return self._photos

    def is_authenticated(self) -> bool:
        return True


@pytest.fixture
def auth_manager():
    """Provide a fake auth manager suitable for running in CI without credentials."""
    return FakeAuthManager()


@pytest.fixture
def drive_manager(auth_manager):
    """Provide a DriveManager wired to a fake Drive service."""
    return DriveManager(auth_manager.get_drive_service())

﻿import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

