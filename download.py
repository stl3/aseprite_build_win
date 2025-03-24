import requests
import os
import zipfile

ASEPRITE_REPO = "aseprite/aseprite"
SKIA_REPO = "aseprite/skia"

ASEPRITE_VERSION = "v1.3.13"  # Manually set Aseprite version
SKIA_VERSION = "m102-861e4743af"  # Manually set Skia version

def download_and_extract_skia(version, output_dir="src/skia"):
    """Downloads and extracts the specified Skia release for Windows."""
    filename = "Skia-Windows-Release-x64.zip"
    url = f"https://github.com/{SKIA_REPO}/releases/download/{version}/{filename}"

    os.makedirs(output_dir, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    zip_path = os.path.join("src", filename)
    with open(zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(output_dir)

    os.remove(zip_path)

def clone_aseprite(version, output_dir="src/aseprite"):
    """Clones the Aseprite repository at the specified tag."""
    os.makedirs(output_dir, exist_ok=True)
    clone_url = f"https://github.com/{ASEPRITE_REPO}.git"
    os.system(f"git clone -b {version} --depth 1 {clone_url} {output_dir}")
    os.system(f"cd {output_dir} && git submodule update --init --recursive")

if __name__ == "__main__":
    clone_aseprite(ASEPRITE_VERSION)
    download_and_extract_skia(SKIA_VERSION)

    with open("version.txt", "w") as f:
        f.write(ASEPRITE_VERSION)
