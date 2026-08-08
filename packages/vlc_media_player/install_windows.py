import os
import platform
import re
import urllib.request
import sys
import shutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sdpkg import download_file, fetch_contents, extract_zip, copy_directory_contents, remove_directory


DOWNLOAD_PAGE = "https://www.videolan.org/vlc/download-windows.html"


def main():
    app_dir = os.path.dirname(__file__)
    # Determine Windows architecture
    machine = platform.machine().lower()

    if machine in ("amd64", "x86_64"):
        platform_name = "win64"
    elif machine in ("arm64", "aarch64"):
        platform_name = "winarm64"
    elif machine in ("x86", "i386", "i686"):
        platform_name = "win32"
    else:
        raise RuntimeError(f"Unsupported Windows architecture: {machine}")

    # Fetch official VideoLAN download page
    html = fetch_contents(DOWNLOAD_PAGE)

    # Find the ZIP corresponding to this architecture.
    pattern = (
        rf'href=[\'"]([^\'"]*/{platform_name}/'
        rf'vlc-[^\'"]+-{platform_name}\.zip)[\'"]'
    )

    matches = re.findall(pattern, html, re.IGNORECASE)

    if not matches:
        raise RuntimeError(
            f"Could not find VLC ZIP for Windows architecture: {platform_name}"
        )

    url = matches[0]

    # Handle protocol-relative URLs (//get.videolan.org/...)
    if url.startswith("//"):
        url = "https:" + url

    filename = os.path.basename(url)
    destination = os.path.join(app_dir, filename)

    print(f"Detected architecture: {platform_name}")
    print(f"Download URL: {url}")
    print(f"Downloading to: {destination}")

    download_file(url, destination)

    print("Download complete.")
    print("Extracting VLC media player...")
    vlc_dir = os.path.join(app_dir, "vlc_media_player_tmpextract")
    extract_zip(destination, vlc_dir)
    print("Extraction complete!")
    print("Moving VLC folder...")
    real_vlc_dir = os.path.join(app_dir, "vlc_mp")
    copy_directory_contents(os.path.join(vlc_dir, os.listdir(vlc_dir)[0]), real_vlc_dir)
    print("Cleaning up...")
    remove_directory(vlc_dir)
    print("Finished!!!")

if __name__ == "__main__":
    main()
