import difflib
import re
import os
import os.path as p

from sorter import find_file_path, print_progress_bar

# The threshold for how similar two files need to be to be considered similar.
# 1 means they are the same, 0 means they are completely different.
SIMILARITY_THRESHOLD = 0.8


def strip_all_whitespace(lines):
    stripped_lines = []
    for line in lines:
        stripped_lines.append(re.sub(r"[\n\t\s]+", "", line) + '\n')
    return stripped_lines


def diff_count(diff):
    count = 0
    for line in diff:
        if line.startswith('+ '):
            count += 1
        # lines with one char difference are probably the same
        # - program: Assignment 2-A
        # ? ^
        # + Program: Assignment 2-A
        # ? ^
        if line.startswith('? '):
            count -= 1

    return count


def diff_ratio(diff):
    '''
    Returns a ratio of how similar the two files are.
    1 means they are the same, 0 means they are completely different.
    '''
    count = 0

    for line in diff:
        if line.startswith('- '):
            continue
        if line.startswith('? '):
            continue
        count += 1

    changed_lines = diff_count(diff)

    if changed_lines == 0:
        return 1

    return 1 - changed_lines / count


def get_all_paths(file_name: str, dirs) -> list:
    paths = []
    for dir in dirs:
        file_path = find_file_path(file_name, dir)
        if file_path is not None:
            paths.append(file_path)
    return paths


def get_contents_of_file(file_name: str) -> list:
    contents = open(file_name, 'r').readlines()
    contents = strip_all_whitespace(contents)
    return contents


def calculate_complexity_steps(len: int) -> int:
    sum = 0
    for i in range(1, len):
        sum += i
    return sum*2


def compare_all_files(files: dict) -> list[tuple[str, str, float]]:
    similar_pairs = []
    counter = 0
    steps = calculate_complexity_steps(len(files))
    for i, (name, content) in enumerate(files.items()):
        if i == len(files) - 1:
            break
        for j, (name2, content2) in enumerate(files.items()):
            if j <= i:
                continue
            counter += 2
            print_progress_bar(counter, steps, prefix='Progress:', suffix='Complete')

            diff = difflib.ndiff(content, content2)
            inverse_diff = difflib.ndiff(content2, content)

            diff_list = list(''.join(diff).splitlines())
            inverse_diff_list = list(''.join(inverse_diff).splitlines())

            max_ratio = max(diff_ratio(diff_list), diff_ratio(inverse_diff_list))
            if max_ratio > SIMILARITY_THRESHOLD:
                similar_pairs.append((name, name2, max_ratio*100))

    return similar_pairs


if __name__ == '__main__':

    dirs = os.listdir('.')
    dirs = [dir for dir in dirs if p.isdir(dir)]
    print("Pick a directory to compare")
    for i, dir in enumerate(dirs):
        print(f"{i}: {dir}")
    choice = input("Enter a number: ")
    os.chdir(dirs[int(choice)])

    file_names = ['messageDigest435.cpp', 'rsa435.cc']

    print("Comparing files: ", file_names)

    dirs = os.listdir('.')
    dirs = [dir for dir in dirs if p.isdir(dir)]
    dirs = [dir for dir in dirs if ',' in dir]
    print(f"Checking {len(dirs)} directories")

    # find all the paths to all the files for each file name
    # structure: [[path1, path2, path3], [path1, path2, path3], [path1, path2, path3]]
    for file_n in file_names:
        paths = get_all_paths(file_n, dirs)
        files_and_contents = {}
        for path in paths:
            files_and_contents[path] = get_contents_of_file(path)
        print(f"Found {len(files_and_contents)} files for {file_n}")
        print("Comparing files...")
        similar_pairs = compare_all_files(files_and_contents)
        print(f"Found {len(similar_pairs)} similar pairs for {file_n}")
        for pair in similar_pairs:
            print(pair)
