# -*- coding: utf-8 -*-
import platform
from urllib.request import urlretrieve
import tarfile
import shutil
import os
import subprocess
import progressbar

pbar = None


def get_platform():
    """Determines user's OS and Architecture
    Based on platform.system(), platform.machine(), and platform.processor (for Mac M* series)
    :return: System and Machine info (e.g. ["win", "x64"] or ["linux", "arm"])
    """
    system = platform.system().lower()
    machine = platform.machine().lower()
    processor = platform.processor().lower()

    if "win" in system:
        system = "win"
        if "64" in machine:
            machine = "x64"
        if "86" in machine:
            machine = "x86"
        return system, machine

    if "mac" in system:
        system = "mac"
        if "64" in machine:
            machine = "x64"
        if "86" in machine:
            machine = "x86"
        if "arm" in machine or "arm" in processor:
            machine = "arm64"
        return system, machine

    if "linux" in system:
        system = "linux"
        if "64" in machine:
            machine = "x64"
        if "86" in machine:
            machine = "x86"
        if "arm" in machine:
            machine = "arm"
        if "musl" in machine:
            machine = "musl"
        return system, machine


def build_version(build):
    """Builds out the download link based on the user's OS and Architecture
    :return: Returns the complete URL of the download link
    (e.g. https://github.com/Kareadita/Kavita/releases/latest/download/kavita-win-x64.tar.gz)
    """
    url = f'https://github.com/Kareadita/Kavita/releases/latest/download/kavita-{build[0]}-{build[1]}.tar.gz'
    return url


def release_version():
    """Determines the latest release version of Kavita
    Based on latest tag
    :return: "v*.*.*" (e.g. v.0.8.0)
    """
    repo_url = "https://github.com/Kareadita/Kavita.git"
    output_lines = subprocess.check_output(
        [
            "git",
            "ls-remote",
            "--tags",
            "--refs",
            "--sort=version:refname",
            repo_url,
        ],
        encoding="utf-8",
    ).splitlines()
    last_line_ref = output_lines[-1].rpartition("/")[-1]
    return last_line_ref


def show_progress(block_num, block_size, total_size):
    """Used for wget download progress bar
    :param block_num: Number of blocks
    :param block_size: Size of each block
    :param total_size: Total size in bytes
    """
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None


def download(url, filename, bar):
    """Downloads the latest release
    :param url: The URL from which to download
    :param filename: What the file should be named as
    :param bar: Any custom progressbar functions
    """
    urlretrieve(url, filename, bar)


def extract_tar(filename, exclusion, destPath):
    """extracts the tar file
    :param filename: Name of file/folder to extract
    :param exclusion: Name of file/folder to exclude from extraction
    :param destPath: Where to extract the tar file
    """
    file = tarfile.open(filename, 'r')
    # Get a list of all archived file names from the zip
    listOfFileNames = file.getnames()
    # Iterate over the file names
    for name in listOfFileNames:
        #check the excluding file condition.
        if exclusion in name:
            continue
        file.extract(name, destPath)
    file.close()


def main():
    build = get_platform()
    url = build_version(build)
    version = release_version()
    exclusion = "config"
    filename = f'kavita-{version}.tar.gz'
    source_dir = './Kavita'
    target_dir = '.'

    print(f'Downloading latest Kavita release ({version}) for {build[0]} {build[1]}...')
    download(url, filename, show_progress)

    print('Extracting update...')
    extract_tar(filename, exclusion, target_dir)

    print('Extraction complete.')

    print('Installing update files...')
    shutil.copytree(source_dir, target_dir, dirs_exist_ok = True)

    print('Update files installed.')

    print('Removing temporary files...')
    shutil.rmtree(source_dir, ignore_errors=False, onerror=None)
    os.remove(filename)

    print('Temporary files removed.')
    print('Update complete.')
    k=input("press enter to exit")


main()
