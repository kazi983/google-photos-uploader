from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys

import requests
from PIL import Image
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


TOKEN_FILE = (
    Path.home()
    / ".config"
    / "google-photos"
    / "token.json"
)

UPLOAD_URL = "https://photoslibrary.googleapis.com/v1/uploads"
BATCH_CREATE_URL = (
    "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"
)

SCOPE = "https://www.googleapis.com/auth/photoslibrary.appendonly"


def get_credentials():
    credentials = Credentials.from_authorized_user_file(
        TOKEN_FILE,
        scopes=[SCOPE],
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        TOKEN_FILE.write_text(credentials.to_json())
        TOKEN_FILE.chmod(0o600)

    return credentials


def get_birth_time(file_path: Path) -> datetime:
    result = subprocess.run(
        [
            "stat",
            "-c",
            "%w",
            str(file_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    birth_time = result.stdout.strip()

    if birth_time == "-":
        raise RuntimeError(
            f"Birth time is not available: {file_path}"
        )

    return datetime.fromisoformat(birth_time)


def add_exif_creation_time(
    source: Path,
    destination: Path,
    creation_time: datetime,
):
    with Image.open(source) as image:
        exif = image.getexif()

        # EXIF DateTime
        exif[306] = creation_time.strftime(
            "%Y:%m:%d %H:%M:%S"
        )

        # EXIF DateTimeOriginal
        exif[36867] = creation_time.strftime(
            "%Y:%m:%d %H:%M:%S"
        )

        # EXIF DateTimeDigitized
        exif[36868] = creation_time.strftime(
            "%Y:%m:%d %H:%M:%S"
        )

        # EXIF OffsetTimeOriginal
        if creation_time.utcoffset() is not None:
            offset = creation_time.strftime("%z")
            offset = f"{offset[:3]}:{offset[3:]}"
            exif[36881] = offset
            exif[36882] = offset

        image.save(
            destination,
            format="PNG",
            exif=exif.tobytes(),
        )


def upload_file(
    file_path: Path,
    credentials: Credentials,
):
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/octet-stream",
        "X-Goog-Upload-Content-Type": "image/png",
        "X-Goog-Upload-File-Name": file_path.name,
        "X-Goog-Upload-Protocol": "raw",
    }

    with file_path.open("rb") as file:
        response = requests.post(
            UPLOAD_URL,
            headers=headers,
            data=file,
        )

    response.raise_for_status()

    return response.text


def create_media_item(
    file_path: Path,
    upload_token: str,
    credentials: Credentials,
):
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
    }

    body = {
        "newMediaItems": [
            {
                "simpleMediaItem": {
                    "fileName": file_path.name,
                    "uploadToken": upload_token,
                }
            }
        ]
    }

    response = requests.post(
        BATCH_CREATE_URL,
        headers=headers,
        json=body,
    )

    response.raise_for_status()

    return response.json()


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            f"Usage: {sys.argv[0]} <image>"
	)

    image_file = Path(sys.argv[1]).expanduser()

    if not image_file.is_file():
        raise FileNotFoundError(image_file)

    birth_time = get_birth_time(image_file)

    print(f"Original file: {image_file}")
    print(f"Birth time:    {birth_time.isoformat()}")

    credentials = get_credentials()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / image_file.name

        print("Embedding EXIF DateTimeOriginal...")

        add_exif_creation_time(
            image_file,
            temp_file,
            birth_time,
        )

        print(f"Uploading:     {temp_file}")

        upload_token = upload_file(
            temp_file,
            credentials,
        )

        result = create_media_item(
            temp_file,
            upload_token,
            credentials,
        )

    print("\nUpload successful.")
    print(result)


if __name__ == "__main__":
    main()
