# Dependencies
* Python 3.6+
* bencode.py

# Script Setup
`pip install bencode.py` 


# Usage
    torrent-mover.py [-h] --src SRC --dst DST [--no-backup] sessions_folder

    positional arguments:
    sessions_folder  This is the rTorrent sessions folder

    options:
    -h, --help
    --src SRC        Set source path to change from
    --dst DST        Set destination path to change to
    --no-backup      Don't create a backup folder for sessions data

    Example: python torrent-mover.py --src /downloads/Temp/ --dst /downloads/Movies/ /config/rTorrent/session
