# Practice 6: Directory Management
# Covers: os.mkdir(), os.listdir(), os.getcwd(), pathlib.Path

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


def show_current_directory():
    print("os.getcwd():", os.getcwd())
    print("Path.cwd():", Path.cwd())


def create_directories():
    new_dir = BASE_DIR / "test_folder"
    sub_dir = new_dir / "sub_folder"

    new_dir.mkdir(exist_ok=True)
    sub_dir.mkdir(exist_ok=True)
    print(f"Created: {new_dir}")
    print(f"Created: {sub_dir}")

    return new_dir


def list_directory(path):
    entries = os.listdir(path)
    print(f"\nos.listdir('{path}'):")
    for entry in entries:
        full = Path(path) / entry
        kind = "DIR " if full.is_dir() else "FILE"
        print(f"  [{kind}] {entry}")


def create_files_in_dir(directory):
    for i in range(1, 4):
        file_path = directory / f"file{i}.txt"
        file_path.write_text(f"Content of file {i}\n")
    print(f"\nCreated 3 files in {directory}")


def cleanup(directory):
    # Remove files and subdirs recursively
    for item in directory.rglob("*"):
        if item.is_file():
            item.unlink()
    for item in sorted(directory.rglob("*"), reverse=True):
        if item.is_dir():
            item.rmdir()
    directory.rmdir()
    print(f"\nCleaned up: {directory}")


if __name__ == "__main__":
    os.chdir(BASE_DIR)

    show_current_directory()
    test_dir = create_directories()
    create_files_in_dir(test_dir)
    list_directory(BASE_DIR)
    list_directory(test_dir)
    cleanup(test_dir)
