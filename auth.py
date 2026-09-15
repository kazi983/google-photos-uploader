from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRET_FILE = (
    Path.home()
    / ".config"
    / "google-photos"
    / "client_secret.json"
)

TOKEN_FILE = (
    Path.home()
    / ".config"
    / "google-photos"
    / "token.json"
)

SCOPES = [
    "https://www.googleapis.com/auth/photoslibrary.appendonly",
]


def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        SCOPES,
    )

    credentials = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
    )

    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(credentials.to_json())
    TOKEN_FILE.chmod(0o600)

    print(f"Token saved to: {TOKEN_FILE}")


if __name__ == "__main__":
    main()
