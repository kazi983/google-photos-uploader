from pathlib import Path

import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


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


def get_credentials():
    credentials = Credentials.from_authorized_user_file(
        TOKEN_FILE,
        scopes=[
            "https://www.googleapis.com/auth/photoslibrary.appendonly",
        ],
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        TOKEN_FILE.write_text(credentials.to_json())
        TOKEN_FILE.chmod(0o600)

    return credentials


def upload_file(file_path: Path, credentials: Credentials):
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-type": "application/octet-stream",
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

    upload_token = response.text

    print(f"Upload token received for: {file_path.name}")

    return upload_token


def create_media_item(
    file_path: Path,
    upload_token: str,
    credentials: Credentials,
):
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-type": "application/json",
    }

    body = {
        "newMediaItems": [
            {
                "description": "Uploaded from Ubuntu",
                "simpleMediaItem": {
                    "uploadToken": upload_token,
                },
            }
        ]
    }

    response = requests.post(
        BATCH_CREATE_URL,
        headers=headers,
        json=body,
    )

    response.raise_for_status()

    result = response.json()

    print(f"Created media item: {file_path.name}")
    print(result)

    return result


def main():
    file_path = Path.home() / "Pictures/GooglePhotos/upload/test.png"

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    credentials = get_credentials()

    upload_token = upload_file(file_path, credentials)

    create_media_item(
        file_path,
        upload_token,
        credentials,
    )


if __name__ == "__main__":
    main()
