#!/usr/bin/env python

import os
import platform
import subprocess
import sys
import tempfile
import urllib.request
import tarfile
import zipfile
import shutil
import stat

GITLEAKS_VERSION = "8.27.2"
GITLEAKS_BASE_URL = f"https://github.com/gitleaks/gitleaks/releases/download/v{GITLEAKS_VERSION}"
INSTALL_DIR = os.path.expanduser("~/.local/bin")
TARGET_BINARY_NAME = "gitleaks.exe" if platform.system() == "Windows" else "gitleaks"

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

def is_enabled():
    try:
        output = subprocess.check_output(["git", "config", "--bool", "gitleaks.enabled"], text=True).strip()
        return output == "true"
    except subprocess.CalledProcessError:
        return False

def is_gitleaks_installed():
    return shutil.which("gitleaks") is not None

def download_and_extract(archive_url, filename):
    tmpdir = tempfile.mkdtemp()
    archive_path = os.path.join(tmpdir, filename)
    print(f"Завантаження: {archive_url}")
    urllib.request.urlretrieve(archive_url, archive_path)

    if filename.endswith(".tar.gz"):
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(tmpdir)
    elif filename.endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
    else:
        print("Невідомий формат архіву.")
        sys.exit(1)

    for root, _, files in os.walk(tmpdir):
        for file in files:
            full_path = os.path.join(root, file)
            if "gitleaks" in file.lower():
                os.chmod(full_path, os.stat(full_path).st_mode | stat.S_IEXEC)
                print("Знайдено файл:", full_path)
                return full_path, tmpdir  # повертаємо і файл, і папку

    print("Не знайдено виконуваного файлу gitleaks.")
    sys.exit(1)

def install_gitleaks():
    system = platform.system()
    arch = platform.machine()
    key = (system, arch)

    if key not in ARCHIVE_MAP:
        print(f"Операційна система або архітектура не підтримується: {system} {arch}")
        sys.exit(1)

    filename = ARCHIVE_MAP[key]
    archive_url = f"{GITLEAKS_BASE_URL}/{filename}"
    binary_path, tmpdir = download_and_extract(archive_url, filename)

    os.makedirs(INSTALL_DIR, exist_ok=True)
    target = os.path.join(INSTALL_DIR, TARGET_BINARY_NAME)
    shutil.copy(binary_path, target)
    os.chmod(target, 0o755)

    shutil.rmtree(tmpdir)  # тепер безпечно видалити тимчасову папку

    print(f"Gitleaks встановлено у {target}")
    if INSTALL_DIR not in os.environ["PATH"]:
        print(f"Попередження: додайте {INSTALL_DIR} до вашого PATH.")

def run_gitleaks_on_directories(directories):
    for directory in directories:
        if not os.path.isdir(directory):
            continue
        print(f"Перевірка каталогу: {directory}")
        try:
            subprocess.run([
                "gitleaks", "detect",
                "--source", directory,
                "--no-git",
                "--no-banner"
            ], check=True)
        except subprocess.CalledProcessError:
            print(f"Виявлено секрети в каталозі: {directory}. Коміт заблоковано.")
            sys.exit(1)

def run_gitleaks():
    directories_to_check = ["."]
    run_gitleaks_on_directories(directories_to_check)

def main():
    if not is_enabled():
        print("Gitleaks перевірка вимкнена. Увімкніть за допомогою: git config gitleaks.enabled true")
        return

    if not is_gitleaks_installed():
        install_gitleaks()

    run_gitleaks()

if __name__ == "__main__":
    main()
