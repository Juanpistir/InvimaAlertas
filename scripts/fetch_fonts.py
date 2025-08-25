# Simple font fetcher for the project.
# Downloads Inter-Regular.ttf and Inter-Bold.ttf into the project's fonts/ directory.

import os
import sys
from pathlib import Path

try:
    import requests
except Exception:
    print("This script requires 'requests'. Install with: pip install requests")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
FONTS_DIR = ROOT / 'fonts'
FONTS_DIR.mkdir(parents=True, exist_ok=True)

# Safer approach: download the official Inter distribution ZIP and extract the TTF files we need.
ZIP_URLS = [
    'https://rsms.me/inter/download/',
    # fallback to GitHub release archive for latest tag (format: releases/download/<tag>/<name>.zip)
    'https://github.com/rsms/inter/releases/latest',
]

import io
import zipfile

def try_download_and_extract(url: str) -> bool:
    try:
        print(f"Attempting download from: {url}")
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        data = r.content
        # If this is HTML (like releases page), try to find a direct zip link inside it
        if not (data.startswith(b'PK') or data.startswith(b"\x50\x4B")):
            # look for a releases asset zip link inside HTML
            text = data.decode('utf-8', errors='ignore')
            import re
            m = re.search(r'href="([^"]+\.zip)"', text)
            if m:
                zip_link = m.group(1)
                if zip_link.startswith('/'):
                    zip_link = 'https://github.com' + zip_link
                print(f"Found zip link in page: {zip_link}")
                r = requests.get(zip_link, stream=True, timeout=30)
                r.raise_for_status()
                data = r.content
            else:
                print("No direct zip found at this URL.")
                return False

        # Try to open as zip
        b = io.BytesIO(data)
        with zipfile.ZipFile(b) as z:
            # list ttf files
            ttf_candidates = [n for n in z.namelist() if n.lower().endswith('.ttf')]
            if not ttf_candidates:
                print("No .ttf files found inside archive.")
                return False
            # prefer Inter-Regular.ttf and Inter-Bold.ttf
            picks = []
            for name in ttf_candidates:
                lower = name.lower()
                if 'inter-regular' in lower or '/regular' in lower or lower.endswith('regular.ttf'):
                    picks.append(name)
                if 'inter-bold' in lower or '/bold' in lower or lower.endswith('bold.ttf'):
                    picks.append(name)
            # fallback pick first two ttf files
            if not picks:
                picks = ttf_candidates[:2]
            # extract selected files
            for member in picks:
                try:
                    out_name = Path(member).name
                    out_path = FONTS_DIR / out_name
                    with z.open(member) as src, open(out_path, 'wb') as dst:
                        dst.write(src.read())
                    print(f"Extracted {out_path}")
                except Exception as e:
                    print(f"Failed to extract {member}: {e}")
        return True
    except Exception as e:
        print(f"Download/extract failed for {url}: {e}")
        return False

success = False
for u in ZIP_URLS:
    if try_download_and_extract(u):
        success = True
        break

if not success:
    print("All attempts failed. You can download Inter manually from https://rsms.me/inter/download/ and place Inter-Regular.ttf into the fonts/ folder.")
else:
    print("Done.")
