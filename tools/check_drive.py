#!/usr/bin/env python3
"""Check the owner's shared Google Drive folder for new clips and download only the new ones.

The owner drops permitted clips (e.g. LunarGaming CC BY videos he downloaded on his PC) into this folder,
because YouTube blocks downloads from our server. State (file ids already seen) lives in page/drive-state.json;
files go to page/media/raw/drive/ (git-ignored). Prints NEW: <path> per new file, or NO NEW FILES.

After a new file: read the YouTube id in its name ([xxxxxxxxxxx]), check the licence with the YouTube Data API,
check frames for webcam/stream overlays, then log the decision in page/permissions.md (rules there).
"""
import json, os, re, sys
import gdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = 'https://drive.google.com/drive/folders/1CTY5GmKDWaqunPvnFI6L3AARCG5I3faO'
STATE = os.path.join(ROOT, 'page/drive-state.json')
OUT = os.path.join(ROOT, 'page/media/raw/drive')


def main():
    os.makedirs(OUT, exist_ok=True)
    seen = json.load(open(STATE)) if os.path.exists(STATE) else {}
    files = gdown.download_folder(url=FOLDER, skip_download=True, quiet=True) or []
    new = 0
    for f in files:
        if f.id in seen: continue
        name = os.path.basename(f.path)
        safe = re.sub(r'[^A-Za-z0-9._\[\]-]+', '_', name)[-120:]
        dest = os.path.join(OUT, safe)
        gdown.download(id=f.id, output=dest, quiet=True)
        yt = re.search(r'\[([A-Za-z0-9_-]{11})\]', name)
        seen[f.id] = {'name': name, 'file': os.path.relpath(dest, ROOT), 'youtube_id': yt.group(1) if yt else None}
        print('NEW:', os.path.relpath(dest, ROOT), '| youtube id:', seen[f.id]['youtube_id'])
        new += 1
    json.dump(seen, open(STATE, 'w'), indent=1)
    if not new: print('NO NEW FILES')


if __name__ == '__main__':
    sys.exit(main())
