import os
import re
import platform
import subprocess
import tempfile
import tarfile
from urllib.parse import urljoin
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sdpkg import download_file, fetch_contents

DOWNLOAD_PAGE = "https://www.7-zip.org/download.html"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "7zip")


def get_os():
    system = platform.system().lower()

    if system == "windows":
        return "windows"

    if system == "linux":
        return "linux"

    if system == "darwin":
        return "macos"

    raise RuntimeError(
        f"Unsupported operating system: {platform.system()}"
    )


def get_arch():
    machine = platform.machine().lower()

    if machine in ("amd64", "x86_64"):
        return "amd64"

    if machine in ("i386", "i486", "i586", "i686", "x86"):
        return "i686"

    if machine in ("arm64", "aarch64"):
        return "arm64"

    if machine.startswith("arm"):
        return "arm32"

    raise RuntimeError(
        f"Unsupported architecture: {platform.machine()}"
    )


def get_latest_release(html):
    """
    Return the HTML table belonging to the newest 7-Zip release.
    The download page lists newest releases first.
    """

    match = re.search(
        r"<P>\s*<B>\s*Download\s+7-Zip\s+.*?</TABLE>",
        html,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        raise RuntimeError(
            "Could not find latest 7-Zip release"
        )

    return match.group(0)


def get_downloads(html):
    """
    Parse Download links from a release table.
    """

    results = []

    pattern = re.compile(
        r'<A\s+href="([^"]+)">\s*Download\s*</A>'
        r'.*?'
        r'<TD[^>]*>\.([a-zA-Z0-9.]+)</TD>'
        r'.*?'
        r'<TD[^>]*>(.*?)</TD>',
        re.IGNORECASE | re.DOTALL
    )

    for match in pattern.finditer(html):
        href = match.group(1)
        extension = match.group(2).lower()
        description = match.group(3)

        description = re.sub(
            r"<[^>]+>",
            " ",
            description
        )

        description = " ".join(
            description.split()
        ).lower()

        url = urljoin(
            DOWNLOAD_PAGE,
            href
        )

        filename = url.rsplit(
            "/",
            1
        )[-1].lower()

        results.append({
            "url": url,
            "filename": filename,
            "extension": extension,
            "description": description
        })

    return results


def select_download(downloads, os_name, arch):
    """
    Select the correct latest 7-Zip package.
    """

    if os_name == "windows":

        if arch == "amd64":
            candidates = [
                x for x in downloads
                if x["extension"] == "msi"
                and "x64" in x["filename"]
            ]

        elif arch == "i686":
            candidates = [
                x for x in downloads
                if x["extension"] == "msi"
                and "x64" not in x["filename"]
                and "arm64" not in x["filename"]
            ]

        elif arch == "arm64":
            # The current 7-Zip download page has an ARM64
            # EXE, but no ARM64 MSI.
            candidates = [
                x for x in downloads
                if x["extension"] == "exe"
                and "arm64" in x["filename"]
            ]

        else:
            raise RuntimeError(
                f"No Windows 7-Zip package for {arch}"
            )

    elif os_name == "linux":

        names = {
            "amd64": "linux-x64",
            "i686": "linux-x86",
            "arm64": "linux-arm64",
            "arm32": "linux-arm"
        }

        wanted = names.get(arch)

        if wanted is None:
            raise RuntimeError(
                f"No Linux 7-Zip package for {arch}"
            )

        candidates = [
            x for x in downloads
            if x["extension"] == "tar.xz"
            and wanted in x["filename"]
        ]

    elif os_name == "macos":

        candidates = [
            x for x in downloads
            if x["extension"] == "tar.xz"
            and "mac" in x["filename"]
        ]

    else:
        raise RuntimeError(
            f"Unsupported OS: {os_name}"
        )

    if not candidates:
        raise RuntimeError(
            f"Could not find a 7-Zip download for "
            f"{os_name}/{arch}"
        )

    return candidates[0]


def extract_tar_xz(archive, destination):
    os.makedirs(
        destination,
        exist_ok=True
    )

    with tarfile.open(
        archive,
        "r:xz"
    ) as tar:
        tar.extractall(destination)


def install_windows(download):
    """
    Extract the Windows MSI using msiexec.
    """

    with tempfile.TemporaryDirectory(
        prefix="sdpkg_7zip_"
    ) as temp:

        msi_path = os.path.join(
            temp,
            "7zip.msi"
        )

        print("Downloading 7-Zip MSI...")

        download_file(
            download["url"],
            msi_path
        )

        print("Extracting 7-Zip MSI...")

        os.makedirs(
            OUTPUT_DIR,
            exist_ok=True
        )

        result = subprocess.run(
            [
                "msiexec.exe",
                "/a",
                msi_path,
                "/qn",
                f"TARGETDIR={OUTPUT_DIR}"
            ],
            check=False
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"msiexec failed with exit code "
                f"{result.returncode}"
            )


def install_linux(download):
    """
    Extract the Linux .tar.xz archive.
    """

    with tempfile.TemporaryDirectory(
        prefix="sdpkg_7zip_"
    ) as temp:

        archive_path = os.path.join(
            temp,
            "7zip.tar.xz"
        )

        print("Downloading 7-Zip archive...")

        download_file(
            download["url"],
            archive_path
        )

        print("Extracting 7-Zip archive...")

        os.makedirs(
            OUTPUT_DIR,
            exist_ok=True
        )

        extract_tar_xz(
            archive_path,
            OUTPUT_DIR
        )


def install():
    print("Fetching 7-Zip download page...")

    html = fetch_contents(
        DOWNLOAD_PAGE
    )

    print("Finding latest 7-Zip release...")

    release = get_latest_release(
        html
    )

    os_name = get_os()
    arch = get_arch()

    print(f"OS: {os_name}")
    print(f"Architecture: {arch}")

    downloads = get_downloads(
        release
    )

    download = select_download(
        downloads,
        os_name,
        arch
    )

    print(
        f"Selected: {download['url']}"
    )

    if os_name == "windows":
        install_windows(download)

    elif os_name == "linux":
        install_linux(download)

    elif os_name == "macos":
        # macOS also provides a tar.xz build.
        install_linux(download)

    print(
        f"7-Zip installed to: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    install()
