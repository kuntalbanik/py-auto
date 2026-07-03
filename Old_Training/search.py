import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Number of worker threads
WORKERS = 10

def is_allowed_file(file_path, extensions):
    if not extensions:
        return True
    return os.path.splitext(file_path)[1].lower() in extensions

def search_in_file(file_path, pattern):
    try:
        with open(file_path, "r", errors="ignore") as f:
            for line in f:
                if pattern.search(line):
                    return file_path
    except Exception:
        pass
    return None

def collect_files(root_dir):
    file_list = []
    for root, _, files in os.walk(root_dir):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list

def main():
    if len(sys.argv) < 4:
        print("Usage: python search.py <directory> <regex> <ext1,ext2,...>")
        print('Example: python search.py ./ "error|panic" .log,.txt')
        return

    root_dir = sys.argv[1]
    regex_pattern = sys.argv[2]
    ext_input = sys.argv[3]

    # Compile regex
    try:
        pattern = re.compile(regex_pattern)
    except re.error as e:
        print("Invalid regex:", e)
        return

    # Parse extensions
    extensions = set()
    if ext_input:
        for ext in ext_input.split(","):
            ext = ext.strip()
            if not ext.startswith("."):
                ext = "." + ext
            extensions.add(ext.lower())

    files = collect_files(root_dir)

    results = []

    # Multithreaded search
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [
            executor.submit(search_in_file, f, pattern)
            for f in files if is_allowed_file(f, extensions)
        ]

        for future in as_completed(futures):
            result = future.result()
            if result:
                print(result)

if __name__ == "__main__":
    main()