import requests
import os
import zipfile
import sys

ASEPRITE_REPO = "aseprite/aseprite"
SKIA_REPO = "aseprite/skia"

def get_latest_release(repo, release_type="stable"):
    """Fetches the latest release tag from a GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/releases"
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

    os.makedirs(output_dir, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    zip_path = os.path.join("src", filename)
    with open(zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)

    os.remove(zip_path)

def clone_aseprite(tag, output_dir="src/aseprite"):
    """Clones the Aseprite repository at the specified tag."""
    os.makedirs(output_dir, exist_ok=True)
    clone_url = f"https://github.com/{ASEPRITE_REPO}.git"
    os.system(f"git clone -b {tag} --depth 1 {clone_url} {output_dir}")
    os.system(f"cd {output_dir} && git submodule update --init --recursive")

if __name__ == "__main__":
    release_type = sys.argv[1] if len(sys.argv) > 1 else "stable"

    aseprite_tag = get_latest_release(ASEPRITE_REPO, release_type)
    clone_aseprite(aseprite_tag)

    if release_type == "beta":
        skia_tag = get_latest_release(SKIA_REPO, "beta")
    else:
        skia_tag = get_latest_release(SKIA_REPO)

    if skia_tag:
        download_and_extract_skia(skia_tag)
    else:
        print("Warning: No matching Skia release found. Using latest stable Skia.")
        skia_tag = get_latest_release(SKIA_REPO)
        download_and_extract_skia(skia_tag)

    with open("version.txt", "w") as f:
        f.write(aseprite_tag)
