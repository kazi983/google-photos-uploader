# Incident Report: Uploader Silently Failing Since 2026-09-15

**Date:** 2026-10-19

## Summary

The user suspected the GNOME autostart entry for this uploader was not
working. Investigation showed autostart was actually fine; the real cause
was an expired Google OAuth refresh token, which made every upload attempt
fail silently for over a month.

## Background

The autostart entry at `~/.config/autostart/google-photos-uploader.desktop`
launches `watch.sh`, which watches `~/Pictures/GooglePhotos/upload/` with
`inotifywait` and runs `upload.py` on every new screenshot.

## Investigation

1. Confirmed the `.desktop` file content and permissions were correct, and
   `watch.sh` was executable.
2. Checked `journalctl` across all boots since 2026-09-25: the
   `app-gnome-google-photos-uploader-*.scope` unit (generated from the
   `.desktop` file by `systemd-xdg-autostart-generator`) started on every
   single login, with no gaps. Autostart itself was never broken.
3. Checked `~/Pictures/GooglePhotos/uploaded/` (successful uploads) vs.
   `~/Pictures/GooglePhotos/upload/` (pending/failed): the last successful
   upload was 2026-09-15 00:08. Two screenshots from 2026-10-18 and
   2026-10-19 were stuck in the pending folder.
4. `journalctl` showed both of those attempts failing with:
   ```
   google.auth.exceptions.RefreshError: ('invalid_grant: Bad Request', {'error': 'invalid_grant', 'error_description': 'Bad Request'})
   ```
5. `~/.config/google-photos/token.json` had not been modified since its
   creation on 2026-09-14, even though `upload.py` rewrites it on every
   successful refresh (`upload.py:37`). This confirmed the refresh token had
   never successfully refreshed again after the initial auth.

## Root Cause

The Google Cloud project (`Ubuntu2GooglePhotos`) OAuth consent screen was
left in **Testing** publishing status. Refresh tokens issued by an app in
Testing status expire after **7 days**, regardless of use. The token was
created 2026-09-14, and no screenshots were taken again until 2026-10-18 —
well past the 7-day window — so the refresh silently failed from that point
on. The autostart process kept running and watching for files the whole
time; only the upload step inside it was broken.

## Resolution

1. Published the OAuth consent screen to **Production** status
   (Google Cloud Console → Google Auth Platform → Audience →
   "Publish App"). This requires an app homepage URL and a privacy policy
   URL in the Branding tab, which were not previously set.
2. Added `PRIVACY.md` to this repository and used the GitHub repo and
   `PRIVACY.md` blob URL as the homepage / privacy policy URLs, and
   registered `github.com` as an authorized domain.
3. Re-ran `auth.py` to generate a fresh refresh token under the new
   Production-status client. Production-status refresh tokens do not expire
   after 7 days.
4. Manually ran `upload.py` on the two screenshots that had been stuck in
   `~/Pictures/GooglePhotos/upload/` since 2026-10-18 and 2026-10-19, then
   moved them to `uploaded/`.

## Files changed

- `PRIVACY.md` (new) — minimal privacy policy required to publish the OAuth
  consent screen to Production.
- `~/.config/google-photos/token.json` — regenerated with a new refresh
  token (not tracked in git).

## Follow-up / things to watch

- The OAuth consent screen requests a restricted scope
  (`photoslibrary.appendonly`). Since the app is unverified, Google may show
  an "unverified app" warning on future re-auths; this is expected for a
  personal single-user app and can be bypassed via "Advanced".
- There is currently no alerting when an upload fails (the script only logs
  to the journal). A long period of inactivity could mask a future failure
  the same way it did this time.
