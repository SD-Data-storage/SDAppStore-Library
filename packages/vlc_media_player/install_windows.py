import os
import platform
import re
import urllib.request


DOWNLOAD_PAGE = "https://www.videolan.org/vlc/download-windows.html"


def main():
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
    request = urllib.request.Request(
        DOWNLOAD_PAGE,
        headers={"User-Agent": "SDPkg"}
    )

    with urllib.request.urlopen(request) as response:
        html = response.read().decode("utf-8")

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
    destination = os.path.join(os.getcwd(), filename)

    print(f"Detected architecture: {platform_name}")
    print(f"Download URL: {url}")
    print(f"Downloading to: {destination}")

    urllib.request.urlretrieve(url, destination)

    print("Download complete.")


if __name__ == "__main__":
    main()
