#!/usr/bin/env python3
import os
import platform
import subprocess
import sys
import tempfile
import urllib.request
import tarfile
import zipfile
import shutil

GITLEAKS_VERSION = "8.27.2"
GITLEAKS_BASE_URL = f"https://github.com/gitleaks/gitleaks/releases/download/v{GITLEAKS_VERSION}"

ARCHIVE_MAP = {
    ("Linux", "x86_64"): f"gitleaks_{GITLEAKS_VERSION}_linux_x64.tar.gz",
    ("Linux", "i386"): f"gitleaks_{GITLEAKS_VERSION}_linux_x32.tar.gz",
    ("Linux", "armv7l"): f"gitleaks_{GITLEAKS_VERSION}_linux_armv7.tar.gz",
    ("Linux", "aarch64"): f"gitleaks_{GITLEAKS_VERSION}_linux_arm64.tar.gz",
    ("Darwin", "x86_64"): f"gitleaks_{GITLEAKS_VERSION}_darwin_x64.tar.gz",
    ("Darwin", "arm64"): f"gitleaks_{GITLEAKS_VERSION}_darwin_arm64.tar.gz",
    ("Windows", "x86_64"): f"gitleaks_{GITLEAKS_VERSION}_windows_x64.zip",
    ("Windows", "i386"): f"gitleaks_{GITLEAKS_VERSION}_windows_x32.zip",
}

INSTALL_DIR = os.path.expanduser("~/.local/bin")  # можна змінити

def is_enabled():
    try:
        output = subprocess.check_output(["git", "config", "--bool", "gitleaks.enabled"], text=True).strip()
        return output == "true"
    except subprocess.CalledProcessError:
        return False

def is_gitleaks_installed():
    return shutil.which("gitleaks") is not None

def download_and_extract(archive_url, filename):
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = os.path.join(tmpdir, filename)
        print(f"Завантаження {archive_url}...")
        urllib.request.urlretrieve(archive_url, archive_path)

        if filename.endswith(".tar.gz"):
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(tmpdir)
        elif filename.endswith(".zip"):
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                zip_ref.extractall(tmpdir)
        else:
            print("Невідомий тип архіву.")
            sys.exit(1)

        for root, _, files in os.walk(tmpdir):
            for file in files:
                if file == "gitleaks" or (file.startswith("gitleaks") and os.access(os.path.join(root, file), os.X_OK)):
                    temp_bin = os.path.join(tempfile.gettempdir(), "gitleaks_bin")
                    shutil.copy(os.path.join(root, file), temp_bin)
                    return temp_bin

        print("gitleaks не знайдено в архіві.")
        sys.exit(1)

def install_gitleaks():
    system = platform.system()
    arch = platform.machine()
    key = (system, arch)

    if key not in ARCHIVE_MAP:
        print(f"Не підтримується ОС/архітектура: {system} {arch}")
        sys.exit(1)

    filename = ARCHIVE_MAP[key]
    archive_url = f"{GITLEAKS_BASE_URL}/{filename}"

    binary_path = download_and_extract(archive_url, filename)
    os.makedirs(INSTALL_DIR, exist_ok=True)
    target_path = os.path.join(INSTALL_DIR, "gitleaks.exe" if system == "Windows" else "gitleaks")
    shutil.copy(binary_path, target_path)
    os.chmod(target_path, 0o755)

    print(f"Встановлено gitleaks → {target_path}")
    if INSTALL_DIR not in os.environ["PATH"]:
        print(f"Увага: додайте {INSTALL_DIR} до вашого PATH.")

def run_gitleaks():
    try:
        subprocess.run(["gitleaks", "detect", "--no-banner"], check=True)
    except subprocess.CalledProcessError:
        print("Gitleaks виявив потенційні секрети! Коміт відхилено.")
        sys.exit(1)

def main():
    if not is_enabled():
        print("Gitleaks перевірка вимкнена (використай `git config gitleaks.enabled true`)")
        return

    if not is_gitleaks_installed():
        install_gitleaks()

    run_gitleaks()

if __name__ == "__main__":
    main()