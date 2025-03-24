import requests
import os
import zipfile

ASEPRITE_REPO = "aseprite/aseprite"
SKIA_REPO = "aseprite/skia"

def get_latest_release(repo):
    """Fetches the latest release tag from a GitHub repository."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(url)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    return response.json()["tag_name"]

def download_and_extract_skia(tag, output_dir="src/skia"):
    """Downloads and extracts the Skia release for Windows."""
    filename = "Skia-Windows-Release-x64.zip"
    url = f"https://github.com/{SKIA_REPO}/releases/download/{tag}/{filename}"

    os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist

    response = requests.get(url)
    response.raise_for_status()

    zip_path = os.path.join("src", filename)
    with open(zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)

    os.remove(zip_path)  # Clean up the zip file

def clone_aseprite(tag, output_dir="src/aseprite"):
    """Clones the Aseprite repository at the specified tag."""
    os.makedirs(output_dir, exist_ok=True)
    clone_url = f"https://github.com/{ASEPRITE_REPO}.git"
    os.system(f"git clone -b {tag} --depth 1 {clone_url} {output_dir}")
    os.system(f"cd {output_dir} && git submodule update --init --recursive")

if __name__ == "__main__":
    aseprite_tag = get_latest_release(ASEPRITE_REPO)
    skia_tag = get_latest_release(SKIA_REPO)

    clone_aseprite(aseprite_tag)
    download_and_extract_skia(skia_tag)

    with open("version.txt", "w") as f:
        f.write(aseprite_tag) #save the aseprite tag.
