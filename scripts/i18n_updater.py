import contextlib
import os
import subprocess


def get_list_of_files(dir_name: str, extension: str):
    file_list = os.listdir(dir_name)

    result = []
    for entry in file_list:
        full_path = os.path.join(dir_name, entry)
        if os.path.isdir(full_path):
            result = result + get_list_of_files(full_path, extension)
        else:
            if entry[-len(extension) : len(entry)] == extension:
                result.append(full_path)

    return result


@contextlib.contextmanager
def cache_creation():
    # DO NOT cache the line number; the file may change
    cache: dict[str, str] = {}
    for file in get_list_of_files("./", ".po"):
        if os.path.isdir(file):
            continue

        with open(file) as f:
            for line in f.readlines():
                if line.startswith('"POT-Creation-Date: '):
                    cache[file] = line
                    break
    yield
    for file, line_cache in cache.items():
        with open(file, "r+") as f:
            lines = f.readlines()
            # clear file
            f.seek(0)
            f.truncate()

            # find line
            index = [
                lines.index(x) for x in lines if x.startswith('"POT-Creation-Date: ')
            ][0]

            lines[index] = line_cache
            f.writelines(lines)


def main():
    with cache_creation():
        subprocess.run(["django-admin", "makemessages", "-a"])
    subprocess.run(["django-admin", "compilemessages"])


if __name__ == "__main__":
    main()
