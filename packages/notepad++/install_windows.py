import os
import platform
import re
import shutil
import urllib.request
import zipfile
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sdpkg import download_file, fetch_contents, extract_zip, copy_directory_contents, remove_directory


DOWNLOAD_PAGE = "https://notepad-plus-plus.org/downloads/"

def get_latest_version():
    request = urllib.request.Request(
        DOWNLOAD_PAGE,
        headers={"User-Agent": "SDPkg"}
    )

    html = fetch_contents(DOWNLOAD_PAGE)

    match = re.search(
        r'/downloads/v([0-9.]+)/',
        html
    )

    if not match:
        raise RuntimeError(
            "Could not determine the latest Notepad++ version "
            "from the official download page."
        )

    return match.group(1)


def main():
    app_dir = os.path.dirname(__file__)
    machine = platform.machine().lower()

    if machine in ("amd64", "x86_64"):
        package_suffix = "portable.x64.zip"
    elif machine in ("arm64", "aarch64"):
        package_suffix = "portable.arm64.zip"
    elif machine in ("x86", "i386", "i686"):
        package_suffix = "portable.zip"
    else:
        raise RuntimeError(
            f"Unsupported Windows architecture: {machine}"
        )

    version = get_latest_version()

    filename = f"npp.{version}.{package_suffix}"

    url = (
        f"https://github.com/notepad-plus-plus/"
        f"notepad-plus-plus/releases/download/"
        f"v{version}/{filename}"
    )

    download_dir = os.path.join(app_dir, ".download")
    extract_dir = os.path.join(app_dir, ".extract")

    os.makedirs(download_dir, exist_ok=True)

    archive = os.path.join(download_dir, filename)

    print(f"Notepad++ version: {version}")
    print(f"Architecture: {machine}")
    print(f"Download: {url}")

    print("Downloading...")

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "SDPkg"}
    )

    with urllib.request.urlopen(request) as response, open(archive, "wb") as file:
        shutil.copyfileobj(response, file)

    print("Extracting...")

    os.makedirs(extract_dir, exist_ok=True)

    extract_zip(archive, extract_dir)

    print("Copying files...")
    install_dir = os.path.join(app_dir, "Notepad++")

    copy_directory_contents(extract_dir, install_dir)

    print("Cleaning up...")

    remove_directory(download_dir)
    remove_directory(extract_dir)

    print("Notepad++ installed successfully.")


if __name__ == "__main__":
    main()
