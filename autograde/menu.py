import os
import sys
import shutil
from datetime import datetime

from render import to_html
from file_formatter import get_zips_in_dir, get_assignment_name, unzip_assignment, remove_all_old_submissions
from workers import grade_all_students
from common_datamodels import argument
from common_tests import build_test, bin_execution_test


def get_choice(options: list) -> int:
    for i, option in enumerate(options):
        print(f"{i}: {option}")
    choice = input("Enter a number: ")
    while not choice.isdigit() or int(choice) not in range(len(options)):
        print("Invalid choice")
        choice = input("Enter a number: ")
    return int(choice)


def pick_assignment_grader() -> str:
    print("Pick class to grade")
    subjects = os.listdir('grade_functions')
    subjects = [sub for sub in subjects if os.path.isdir(sub)]
    sub_choice = get_choice(subjects)
    assignments = os.listdir('grade_functions')
    assignments = [assignment for assignment in assignments if os.path.isdir(assignment)]
    if len(assignments) == 0:
        print("No assignments found")
        exit(1)
    assign_choice = get_choice(assignments)
    return os.path.join('grade_functions', subjects[sub_choice], assignments[assign_choice])


def fetch_args(args_path):
    args_file = os.path.join(args_path, '/args.txt')
    if not os.path.isfile(args_file):
        print("No args.txt file found")
        exit(1)
    arguments = []
    with open(args_file, 'r') as f:
        for line in f:
            if line[0] == '#':
                continue
            if line.strip() == '':
                continue
            function_name = line.split(':')[0].strip()
            arg_names = [arg.strip() for arg in line.split(':')[1].strip().split(',')]
    pass


def print_args(args=None):
    print("Please specify an argument")
    print("-unzip: unzip assignments in the current directory")


def assignment_zips(force=False):
    zips = get_zips_in_dir()
    zips = ['All', *zips]
    print("Pick an assignment to unzip")
    choice = get_choice(zips)
    if choice == int(0):
        for zip in zips[1:]:
            if force:
                folder_name = get_assignment_name(zip)
                if os.path.isdir(folder_name):
                    shutil.rmtree(get_assignment_name(zip))
            unzip_assignment(zip)
    else:
        if force:
            shutil.rmtree(get_assignment_name(zips[int(choice)]))
        unzip_assignment(zips[int(choice)])


def pick_directory(action: str = 'to build') -> bool:
    dirs = os.listdir('.')
    dirs = [dir for dir in dirs if os.path.isdir(dir)]
    dirs = [dir for dir in dirs if dir != 'zips']
    dirs = ['Exit', *dirs]

    print(f"Pick a directory {action}")
    print("")
    choice = get_choice(dirs)
    if choice == 0:
        return False
    os.chdir(dirs[int(choice)])
    return True


def menu():
    '''
        Arguments:
        -f or -force: remove and rewrite the unzipped files
        -unzip: unzip all the zips in the current directory
    '''
    start_dir = os.getcwd()
    force = False

    # if len(sys.argv) == 1:
    #     print_args()
    #     exit(1)

    if '-force' in sys.argv or '-f' in sys.argv:
        force = True

    if '-d' in sys.argv:
        os.chdir('example')
    else:
        os.chdir('put_zips_here')

    if '-unzip' in sys.argv:
        assignment_zips(force)

    if pick_directory():
        remove_all_old_submissions()
        now = datetime.now()
        results = grade_all_students(build_test)
        print(f"Time to grade: {(datetime.now() - now).total_seconds():.2f}s")
        to_html(results, 'build.html')

        run = input(f"Run executables? [y/N]\n") == 'y'
        if run:
            run_results = grade_all_students(bin_execution_test)
            to_html(run_results, 'run.html')

        os.chdir(start_dir)
        if '-unzip' in sys.argv:
            sys.argv.remove('-unzip')

        menu()

    # if '-p1' in sys.argv:
    #     remove_old_submissions()
    #     now = datetime.now()
    #     results = grade_all_students(grade_part_1)
    #     print(f"Time to grade: {(datetime.datetime.now() - now).total_seconds():.2f}s")
    #     to_html(results, 'part1.html')

    # if '-p2' in sys.argv:
    #     remove_old_submissions()
    #     now = datetime.now()
    #     results = grade_all_students(grade_part_2)
    #     print(f"Time to grade: {(datetime.datetime.now() - now).total_seconds():.2f}s")
    #     to_html(results, 'part2.html')


if __name__ == '__main__':
    os.chdir
    menu()
