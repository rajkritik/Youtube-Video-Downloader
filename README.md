# Youtube-Video-Downloader

Overview
This desktop app downloads entire YouTube playlists in the highest available quality by combining best video and best audio, then remuxes to MP4.

Files are saved inside a per‑playlist folder and named with plain integers: 1 - Title.mp4, 2 - Title.mp4, … (no zero padding).

Thumbnails are not downloaded or embedded; only video and audio are saved.

Requirements
Python 3.8+ installed and on PATH.

yt-dlp installed and on PATH (or callable):

pip:

Windows/Linux/macOS:

pip install -U yt-dlp

or download the standalone binary from the official releases and place it on PATH.

FFmpeg installed and on PATH so yt‑dlp can merge video+audio into MP4:

Windows: download a static build, extract, and add the bin folder to PATH.

Linux/macOS: install via package manager or official builds and ensure ffmpeg is callable from the terminal.

Installation
Save the provided Python script as downloader.py (or any name).

Ensure Python, yt-dlp, and ffmpeg are installed and available on PATH.

Double‑click the script (if file associations allow) or run from terminal:

Windows:

python downloader.py

Linux/macOS:

python3 downloader.py

Usage
Launch the app; the window is resizable and can be maximized.

Paste a YouTube playlist URL into “Playlist URL”.

Pick a “Download folder”; the app creates a subfolder named after the playlist title.

Optional: attach a cookies file in “Cookies file” if the playlist requires login or age‑verification.

Click “Start download”.

Observe progress and logs; “Stop” will try to terminate the active job.

Output details
Folder structure:

PlaylistTitle/

1 - VideoTitle.mp4

2 - VideoTitle.mp4

…

Naming: unpadded numbers via %(playlist_index)d in the output template.

Quality: bestvideo+bestaudio selected, then remuxed to MP4.

No thumbnails: the app does not request or embed thumbnails.

Archive file: archive.txt is stored in the selected download folder to avoid re‑downloading already completed items; delete it to force re‑download.

Getting cookies with a browser extension
If a playlist is private, unlisted with restrictions, age‑gated, or otherwise requires being signed in, export a cookies.txt and attach it in the app.

Microsoft Edge (recommended for Windows)
Open Edge and sign in to YouTube (youtube.com) with the account that has access.

Install a cookies exporter that saves in Netscape cookies.txt format, for example:

“Get cookies.txt LOCALLY” or “cookies.txt” extension (Edge supports Chrome Web Store).

Navigate to youtube.com (ensure the tab is active and logged in).

Click the extension icon and choose Export/Download for the current site (youtube.com).

Save the file as edge_youtube.txt (or any name).

In the app, click “Browse…” in “Cookies file” and select the saved cookies file.

Tips:

Export only for youtube.com to keep the file clean.

Re‑export cookies after changing passwords or logouts.

Keep the file private; it grants the same access as the signed‑in session.

Google Chrome
The same steps as Edge: install a cookies.txt exporter, open youtube.com logged in, export cookies to a cookies.txt file, and attach it in the app.

Firefox
Install a cookies.txt exporter add‑on that supports Netscape format.

Open youtube.com logged in, export cookies, save as a .txt file, then attach it in the app.

Common scenarios
Private course playlists: attach cookies.txt so yt‑dlp can authenticate on requests.

Age‑restricted content: cookies often resolve the age gate without extra flags.

Rate limits or network hiccups: downloads retry internally; use “Stop” to cancel and rerun later.

Troubleshooting
“yt-dlp not found”: confirm yt-dlp runs in a terminal (yt-dlp --version); add it to PATH or use pip install -U yt-dlp.

“ffmpeg not found”: confirm ffmpeg runs in a terminal (ffmpeg -version); add it to PATH.

Merge failures or rare MP4 incompatibilities: switch to MKV temporarily by changing the script’s --merge-output-format to mkv, or constrain formats with yt‑dlp’s -S sort (advanced).

Re‑download specific items: delete archive.txt in the download folder, then run again (this will redownload everything unless selective flags are added).

Slow segmented streams: increase or decrease CONCURRENT in the script (default 8) to match local bandwidth and server limits.

Keyboard shortcuts and tips
Copy/paste work as expected in all fields.

The log view autoscrolls to the newest output.

The window can be resized or maximized; the log area expands with the window.

Privacy and security
The cookies file contains authentication information; store it securely and do not share it.

Remove cookies from the app when no longer needed by clearing the field.

Revoke sessions by signing out from the browser if a cookies file is compromised.

Customization
Destination structure: change TEMPLATE in the script to suit preferred naming and folders.

Numbering style: the script uses %(playlist_index)d for plain integers; switch to %(playlist_autonumber)d to number in actual download order when using reversed/sliced playlists.

Concurrency: adjust CONCURRENT for HLS/DASH segmented streams.

License
This script depends on yt‑dlp and ffmpeg. Follow their licenses and site terms.

If a prebuilt cookies exporter is not available in a store, a manual export from developer tools is possible but more involved; using a cookies.txt exporter extension is the simplest method.

