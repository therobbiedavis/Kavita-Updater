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
    url = f'https://github.com/Kareadita/Kavita/releases/latest/download/kavita-{build[0]}-{build[1]}.tar.gz'
    return url


def release_version():
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


def copy(src, dst):
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    shutil.copyfile(src, dst)


def main():
    build = get_platform()
    url = build_version(build)

    version = release_version()
    filename = f'kavita-{version}.tar.gz'
    print(f'Downloading latest Kavita release ({version}) for {build[0]} {build[1]}...')
    urlretrieve(url, filename, show_progress)
    # wget.download(url, bar=bar_custom)
    print('Extracting update...')
    file = tarfile.open(filename, 'r')
    # Get a list of all archived file names from the zip
    listOfFileNames = file.getnames()
    # Iterate over the file names
    for name in listOfFileNames:
        #check the excluding file condition.
        if 'config' in name:
            continue
        file.extract(name, '.')
    file.close()
    print('Extraction complete.')
    source_dir = './Kavita'
    target_dir = '.'
    print('Installing update files...')
    # copy(source_dir, target_dir)
    shutil.copytree(source_dir, target_dir, dirs_exist_ok = True)
    print('Update files installed.')
    print('Removing temporary files...')
    shutil.rmtree(source_dir, ignore_errors=False, onerror=None)
    os.remove(filename)
    print('Temporary files removed.')
    print('Update complete.')
    k=input("press enter to exit")


main()
