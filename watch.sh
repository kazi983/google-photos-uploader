#!/bin/bash

set -euo pipefail

WATCH_DIR="$HOME/Pictures/GooglePhotos/upload"
UPLOADED_DIR="$HOME/Pictures/GooglePhotos/uploaded"
PROJECT_DIR="$HOME/bin/google-photos-uploader"

mkdir -p "$WATCH_DIR"
mkdir -p "$UPLOADED_DIR"

inotifywait -m \
    -e close_write,moved_to \
    --format '%w%f' \
    "$WATCH_DIR" |
while IFS= read -r file; do

    case "$file" in
        *.png|*.PNG)
            echo "New screenshot: $file"

            if "$PROJECT_DIR/.venv/bin/python" \
                "$PROJECT_DIR/upload.py" \
                "$file"; then

                mv -- "$file" "$UPLOADED_DIR/"
                echo "Uploaded: $file"
            else
                echo "Upload failed: $file" >&2
            fi
            ;;
    esac

done
