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
INSTALL_DIR = os.path.expanduser("~/.local/bin")

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
    with tempfile.TemporaryDirectory() as tmpdir:
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
                if file == "gitleaks" or file == "gitleaks.exe":
                    return os.path.join(root, file)

        print("Не знайдено бінарника gitleaks.")
        sys.exit(1)

def install_gitleaks():
    system = platform.system()
    arch = platform.machine()
    key = (system, arch)

    if key not in ARCHIVE_MAP:
        print(f"Не підтримується: {system} {arch}")
        sys.exit(1)

    filename = ARCHIVE_MAP[key]
    archive_url = f"{GITLEAKS_BASE_URL}/{filename}"
    binary_path = download_and_extract(archive_url, filename)

    os.makedirs(INSTALL_DIR, exist_ok=True)
    target = os.path.join(INSTALL_DIR, "gitleaks.exe" if system == "Windows" else "gitleaks")
    shutil.copy(binary_path, target)
    os.chmod(target, 0o755)

    print(f"Gitleaks встановлено → {target}")
    if INSTALL_DIR not in os.environ["PATH"]:
        print(f"Увага: додайте {INSTALL_DIR} до вашого PATH.")

def run_gitleaks():
    allowed_folders = ["src", "app", "scripts"]  # ← змінити під свій проект

    # Отримати staged файли
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], stdout=subprocess.PIPE, text=True)
    files = result.stdout.strip().split('\n')
    files = [f for f in files if any(f.startswith(folder + "/") for folder in allowed_folders)]

    if not files:
        print("Немає змінених файлів у дозволених директоріях.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        for f in files:
            dest_path = os.path.join(tmpdir, f)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            try:
                with open(dest_path, "wb") as out:
                    subprocess.run(["git", "show", f":{f}"], stdout=out, check=True)
            except subprocess.CalledProcessError:
                print(f"Не вдалося отримати staged-версію файлу: {f}")
                sys.exit(1)

        try:
            subprocess.run([
                "gitleaks", "detect",
                "--source", tmpdir,
                "--no-git",
                "--no-banner"
            ], check=True)
        except subprocess.CalledProcessError:
            print("Gitleaks виявив секрети у staged-файлах. Коміт заблоковано.")
            sys.exit(1)

def main():
    if not is_enabled():
        print("Gitleaks перевірка вимкнена. Увімкни: git config gitleaks.enabled true")
        return

    if not is_gitleaks_installed():
        install_gitleaks()

    run_gitleaks()

if __name__ == "__main__":
    main()
