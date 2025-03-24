import requests
import os
import zipfile
import sys
import re
from bs4 import BeautifulSoup  # import beautiful soup.

ASEPRITE_REPO = "aseprite/aseprite"
SKIA_REPO = "aseprite/skia"

def get_latest_aseprite_release(release_type="stable"):
    """Fetches the latest Aseprite release tag."""
    url = f"https://api.github.com/repos/{ASEPRITE_REPO}/releases"
    response = requests.get(url)
    response.raise_for_status()
    releases = response.json()

    for release in releases:
        if release_type == "stable" and "beta" not in release["tag_name"].lower():
            return release["tag_name"]
        elif release_type == "beta" and "beta" in release["tag_name"].lower():
            return release["tag_name"]

    return None

def download_and_extract_skia(tag, output_dir="src/skia"):
    """Downloads and extracts the Skia release for Windows."""
    filename = "Skia-Windows-Release-x64.zip"
    url = f"https://github.com/{SKIA_REPO}/releases/download/{tag}/{filename}"

    print(f"Skia Download URL: {url}")  # debug print

    os.makedirs(output_dir, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    zip_path = os.path.join("src", filename)
    with open(zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)

    os.remove(zip_path)

def clone_aseprite(tag, output_dir="src/aseprite", release_type="stable"):
    """Clones or downloads the Aseprite repository at the specified tag."""
    os.makedirs(output_dir, exist_ok=True)
    if release_type == "stable":
        clone_url = f"https://github.com/{ASEPRITE_REPO}.git"
        os.system(f"git clone -b {tag} --depth 1 {clone_url} {output_dir}")
        os.system(f"cd {output_dir} && git submodule update --init --recursive")
    else:  # beta
        url = f"https://github.com/{ASEPRITE_REPO}/releases/download/{tag}/Aseprite-{tag}-Source.zip"
        print(f"Aseprite Download URL: {url}")  # debug print
        response = requests.get(url)
        response.raise_for_status()
        zip_path = os.path.join("src", "Aseprite.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)
        os.remove(zip_path)

def get_latest_skia_tag(release_type="stable"):
    """Gets the latest Skia tag based on release type."""
    if release_type == "stable":
        url = "https://github.com/aseprite/skia/releases/latest"
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
        redirected_url = response.url
        tag = redirected_url.split("/tag/")[1]
        return tag
    else:  # beta
        url = "https://github.com/aseprite/skia/releases"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")  # Use beautiful soup to parse the html.
        release_links = soup.find_all("a", href=True)  # find all a tags with href.
        for link in release_links:
            if "beta" in link.text.lower():  # find the link with beta in the text.
                match = re.search(r'/tag/([a-zA-Z0-9-]+)', link["href"])  # extract the tag from the href.
                if match:
                    return match.group(1)
        return None  # Return None if no beta release is found

if __name__ == "__main__":
    release_type = sys.argv[1] if len(sys.argv) > 1 else "stable"

    aseprite_tag = get_latest_aseprite_release(release_type)
    clone_aseprite(aseprite_tag, release_type=release_type)

    skia_tag = get_latest_skia_tag(release_type)

    if skia_tag:
        print(f"Aseprite {release_type} tag: {aseprite_tag}")
        print(f"Skia {release_type} tag: {skia_tag}")
        download_and_extract_skia(skia_tag)
    else:
        print("Warning: No matching Skia release found. Using latest stable Skia.")
        skia_tag = get_latest_skia_tag()
        print(f"Aseprite {release_type} tag: {aseprite_tag}")
        print(f"Skia stable tag: {skia_tag}")
        download_and_extract_skia(skia_tag)

    with open("version.txt", "w") as f:
        f.write(aseprite_tag)
