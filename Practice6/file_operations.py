# Practice 6: File Handling Operations
# Covers: read, write, append, copy, delete file operations

import os

FILENAME = "sample.txt"


# 1. Write mode (w) - creates or overwrites file
def write_file():
    with open(FILENAME, "w") as f:
        f.write("Hello, World!\n")
        f.write("Python file handling\n")
        f.write("Line 3\n")
    print(f"Written to {FILENAME}")


# 2. Read mode (r) - read entire file
def read_file():
    with open(FILENAME, "r") as f:
        content = f.read()
    print("read():", repr(content))


# 3. readline() - read one line at a time
def read_lines_one_by_one():
    with open(FILENAME, "r") as f:
        line = f.readline()
        while line:
            print("readline():", repr(line))
            line = f.readline()


# 4. readlines() - read all lines into a list
def read_all_lines():
    with open(FILENAME, "r") as f:
        lines = f.readlines()
    print("readlines():", lines)


# 5. Append mode (a) - add to existing file without overwriting
def append_file():
    with open(FILENAME, "a") as f:
        f.write("Appended line\n")
    print(f"Appended to {FILENAME}")


# 6. Exclusive creation mode (x) - fails if file already exists
def exclusive_create():
    new_file = "new_exclusive.txt"
    try:
        with open(new_file, "x") as f:
            f.write("Created with x mode\n")
        print(f"Created {new_file}")
    except FileExistsError:
        print(f"{new_file} already exists — x mode failed as expected")


# 7. Copy file manually
def copy_file():
    copy_name = "sample_copy.txt"
    with open(FILENAME, "r") as src:
        content = src.read()
    with open(copy_name, "w") as dst:
        dst.write(content)
    print(f"Copied {FILENAME} -> {copy_name}")


# 8. Delete file
def delete_file():
    to_delete = "new_exclusive.txt"
    if os.path.exists(to_delete):
        os.remove(to_delete)
        print(f"Deleted {to_delete}")
    else:
        print(f"{to_delete} does not exist")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    write_file()
    read_file()
    read_lines_one_by_one()
    read_all_lines()
    append_file()
    exclusive_create()
    exclusive_create()   # second call to show FileExistsError
    copy_file()
    delete_file()
