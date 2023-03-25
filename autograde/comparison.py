import difflib
import re
import os
import os.path as p
import shutil

from render import print_progress_bar
from file_formatter import find_file_path, find_files_by_extension

# The threshold for how similar two files need to be to be considered similar.
# 1 means they are the same, 0 means they are completely different.
SIMILARITY_THRESHOLD = 0.88


def strip_all_whitespace(lines):
    stripped_lines = []
    for line in lines:
        striped_line = re.sub(r"[\n\t\s]+", "", line)
        if len(striped_line) > 0:
            stripped_lines.append(striped_line + '\n')
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
        file_path = find_files_by_extension(file_name, dir)
        if len(file_path) > 0:
            paths.append(file_path[0])
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
    total = len(files)
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
            total += max_ratio
            if max_ratio > SIMILARITY_THRESHOLD:
                similar_pairs.append((name, name2, max_ratio*100))
    if steps > 0:
        print(f"Average similarity: {(total/(counter/2))*100}")

    return similar_pairs


def render_results(similar_pairs):
    for pair in similar_pairs:
        student1 = pair[0].split(os.path.sep)[0]
        student2 = pair[1].split(os.path.sep)[0]
        file1 = os.path.basename(pair[0])
        file2 = os.path.basename(pair[1])
        print(f"Similarity: {pair[2]:.2f}% Student 1: {student1} Student 2: {student2}")
        print(f"File 1: {file1} File 2: {file2}")


def copy_files(similar_pairs, file_n):
    if not os.path.exists('zz_similar'):
        os.mkdir('zz_similar')
    else:
        shutil.rmtree('zz_similar')
        os.mkdir('zz_similar')
    for i, pair in enumerate(similar_pairs):
        student1 = pair[0].split(os.path.sep)[0]
        student2 = pair[1].split(os.path.sep)[0]
        file1 = os.path.basename(pair[0])
        file2 = os.path.basename(pair[1])
        if not os.path.exists(f'zz_similar/pair{i}/'):
            os.mkdir(f'zz_similar/pair{i}/')

        shutil.copy(pair[0], f'zz_similar/pair{i}/{student1}-{file1}')
        shutil.copy(pair[1], f'zz_similar/pair{i}/{student2}-{file2}')


if __name__ == '__main__':
    os.chdir('put_zips_here')
    dirs = os.listdir('.')
    dirs = [dir for dir in dirs if p.isdir(dir)]
    print("Pick a directory to compare")
    for i, dir in enumerate(dirs):
        print(f"{i}: {dir}")
    choice = input("Enter a number: ")
    os.chdir(dirs[int(choice)])

    SIMILARITY_THRESHOLD = int(input(f"Enter a similarity threshold 0-100 (default:{SIMILARITY_THRESHOLD}): "))

    file_names = ['.cpp', '.h', '.hpp']
    ignore_files = ['rational']

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
            if any([name in os.path.basename(path).lower() for name in ignore_files]):
                continue
            files_and_contents[path] = get_contents_of_file(path)
        print(f"Found {len(files_and_contents)} files for {file_n}")
        if len(files_and_contents) > 0:
            print("Comparing files...")
            similar_pairs = compare_all_files(files_and_contents)
            print(f"Found {len(similar_pairs)} similar pairs for {file_n}")
            render_results(similar_pairs)
            copy_files(similar_pairs, file_n)
