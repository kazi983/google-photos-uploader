# Google Photos Screenshot Uploader

Automatically upload screenshots from Ubuntu to Google Photos.

The application watches a local folder using Linux `inotify`. When a new PNG screenshot is detected, it reads the file's creation time, embeds it as EXIF metadata with the correct timezone, uploads the image to Google Photos, and moves the successfully uploaded file to a separate folder.

## How It Works

```text
Screenshot
    ↓
~/Pictures/GooglePhotos/upload/
    ↓
inotify
    ↓
watch.sh
    ↓
upload.py
    ↓
Google Photos
    ↓
~/Pictures/GooglePhotos/uploaded/
```

The original screenshot is not modified. A temporary copy is created for adding the metadata and uploading.

## Requirements

* Ubuntu or another Linux distribution with `inotify`
* Python 3
* A Google account
* A Google Cloud project
* Google Photos Library API
* Google OAuth 2.0 Desktop application credentials

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd google-photos-uploader
```

### 2. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install google-auth-oauthlib
pip install google-auth-httplib2
pip install google-api-python-client
pip install requests
pip install Pillow
```

### 4. Install `inotify-tools`

```bash
sudo apt install inotify-tools
```

### 5. Configure Google Cloud

Create a Google Cloud project and enable the Google Photos Library API.

Create an OAuth 2.0 Client ID with the application type:

```text
Desktop app
```

Download the client secret JSON file and store it outside the repository:

```bash
mkdir -p ~/.config/google-photos
```

Save it as:

```text
~/.config/google-photos/client_secret.json
```

Do not commit this file to GitHub.

### 6. Authenticate with Google

Run:

```bash
source .venv/bin/activate
python auth.py
```

Complete the Google authentication in your browser.

The OAuth token will be saved to:

```text
~/.config/google-photos/token.json
```

Keep this file private.

### 7. Configure the screenshot folders

Create the folders:

```bash
mkdir -p ~/Pictures/GooglePhotos/upload
mkdir -p ~/Pictures/GooglePhotos/uploaded
```

Configure your screenshot application to save screenshots to:

```text
~/Pictures/GooglePhotos/upload/
```

Successfully uploaded screenshots will be moved to:

```text
~/Pictures/GooglePhotos/uploaded/
```

## Enable Automatic Upload

Make the watcher executable:

```bash
chmod +x ~/bin/google-photos-uploader/watch.sh
```

If the repository is located somewhere else, adjust the path accordingly.

### Create the autostart entry

Create the autostart directory:

```bash
mkdir -p ~/.config/autostart
```

Create:

```text
~/.config/autostart/google-photos-uploader.desktop
```

Add:

```ini
[Desktop Entry]
Type=Application
Name=Google Photos Uploader
Comment=Automatically upload screenshots to Google Photos
Exec=/home/USERNAME/bin/google-photos-uploader/watch.sh
Terminal=false
X-GNOME-Autostart-enabled=true
```

Replace `USERNAME` with your Linux username.

After logging into Ubuntu, `watch.sh` will start automatically and continuously monitor the screenshot directory.

## Directory Structure

The application:

```text
google-photos-uploader/
├── auth.py
├── upload.py
├── watch.sh
├── README.md
└── .gitignore
```

Local credentials:

```text
~/.config/google-photos/
├── client_secret.json
└── token.json
```

Screenshot directories:

```text
~/Pictures/GooglePhotos/
├── upload/
└── uploaded/
```

## Limitations

* Currently supports PNG screenshots.
* Requires Linux `inotify`.
* Requires Google OAuth authentication.
* Requires the Google Photos API.
* The screenshot file must have an available filesystem `Birth` timestamp.
* Screenshots must be saved to the configured `upload` directory.
