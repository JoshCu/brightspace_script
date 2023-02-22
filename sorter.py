from os import listdir, makedirs, rename, remove, chdir, getcwd
from os import path as p
import shutil
import zipfile
import psutil
import traceback

from typing import Callable
from dataclasses import dataclass
from enum import Enum
import os
import sys
import subprocess
import datetime
import asyncio

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# timeout in seconds for each test
TIMEOUT = 120

# list of processes to stop after each part of the assignment
GLOBAL_CLEANUP = []

# give either full path to compiler or just the name of the compiler
# if just the name of the compiler, it will assume it is in the path
COMPILER = "g++"
COMPILER_FLAGS = ["-std=c++17"]
# only reports failures
HIDE_SUCCESS = False


class exit_code(Enum):
    SUCCESS = 0
    ERROR = 1
    NOT_ATTEMPTED = -1


@dataclass
class test_result:
    # if exit code isn't valid, then set it to 1
    result: str = ""
    _exit_code: int = exit_code.NOT_ATTEMPTED.value

    @property
    def exit_code(self):
        return self._exit_code

    @exit_code.setter
    def exit_code(self, value):
        if not any(value == code.value for code in exit_code):
            self._exit_code = 1
        else:
            self._exit_code = value


@dataclass
class part1:
    student_name: str
    rsa_file_found: test_result = None     # type: ignore
    rsa_file_compiles: test_result = None  # type: ignore
    rsa_file_runs: test_result = None      # type: ignore
    keys_file_found: test_result = None    # type: ignore
    grading_builds: test_result = None     # type: ignore
    grading_runs: test_result = None       # type: ignore

    # if you don't do this, the attributes of the class will be shared between all instances
    def __post_init__(self):
        for attr in self.__dict__.keys():
            if self.__annotations__[attr] == test_result:
                setattr(self, attr, test_result())

    # allows you to access the attributes of the class using index like syntax
    def __getitem__(self, items):
        return getattr(self, items)


@dataclass
class part2:
    student_name: str
    message_file_found: test_result = None     # type: ignore
    message_file_compiles: test_result = None  # type: ignore
    one_line_signed: test_result = None        # type: ignore
    two_line_signed: test_result = None        # type: ignore
    bible_part1_signed: test_result = None     # type: ignore
    one_line_verified: test_result = None      # type: ignore
    two_line_verified: test_result = None      # type: ignore
    bible_part1_verified: test_result = None   # type: ignore

    # if you don't do this, the attributes of the class will be shared between all instances
    def __post_init__(self):
        for attr in self.__dict__.keys():
            if self.__annotations__[attr] == test_result:
                setattr(self, attr, test_result())

    # allows you to access the attributes of the class using index like syntax
    def __getitem__(self, items):
        return getattr(self, items)

# funtion to print a progress bar to the console


def print_progress_bar(
        iteration, total, prefix='', suffix='', decimals=1, length=os.get_terminal_size()[0], fill='█',
        printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r)
    """
    length -= len(prefix) + len(suffix) + 11
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def find_AM_PM(path):
    # find the AM or PM in the path
    # if it is not found then return None
    # otherwise return the index of the AM or PM
    if "AM" in path:
        return path.index("AM")
    elif "PM" in path:
        return path.index("PM")
    else:
        raise ValueError(f"AM or PM not found in path {path}")


def extract_date(path):
    # get the date from the path
    # convert it into a datetime object
    # return the datetime object

    # variation in names and formats means we have to do this manually
    # find AM or PM and then work backwards
    start_location = find_AM_PM(path.split(' ')) - 4

    date_list = path.split(' ')[start_location:start_location+5]
    # formatted as Jan 1, 2023 1114 AM

    # manually day and pad the hour but not minutes
    # jfc what is this format brightspace
    month = date_list[0]
    year = date_list[2]
    day = date_list[1][:-1]
    hour = date_list[3][:-2]
    minute = date_list[3][-len(hour):]
    AmPm = date_list[4]

    day = day.zfill(2)
    hour = hour.zfill(2)
    minute = minute.zfill(2)
    # re add the day and hour
    new_date_string = f"{month} {day} {year} {hour} {minute} {AmPm}"

    # comma omitted as we don't re add it after it's removed
    dt = datetime.datetime.strptime(new_date_string, "%b %d %Y %I %M %p")
    return dt


def get_most_recent_path(student_paths):
    # get the most recent path
    most_recent = None
    most_recent_date = None
    for path in student_paths:
        # all brightspace paths start with 12 digits
        # if not then it's a path we've made and we can ignore it
        if not path.split(' ')[0].isnumeric():
            continue
        date = extract_date(path)
        if most_recent_date is None or date > most_recent_date:
            most_recent = path
            most_recent_date = date

    return most_recent


def to_html(results, filename="results.html"):
    # create an html file with the results in a table format
    # one row per student, use the variable names in the dataclass as the column headers
    # use the result and exit_code variables in the test_result dataclass as the values
    # use the exit_code enum to determine the color of the cell
    # green for success, light red for error, yellow for not attempted
    results = sorted(results, key=lambda x: x.student_name)
    headers = results[0].__annotations__.keys()
    with open(filename, 'w') as f:
        # import style sheet freeze.css
        f.write('<link rel="stylesheet" href="../freeze.css">\n')
        f.write('<html><body><table>\n')
        f.write('<tr>')
        for header in headers:
            f.write(f'<th>{header}</th>')
        f.write('</tr>\n')
        for result in results:
            f.write('<tr>')
            for header in headers:
                value = getattr(result, header)
                if isinstance(value, test_result):
                    # strip all non utf-8 characters
                    value.result = value.result.encode('ascii', 'ignore').decode('ascii')
                    if value.exit_code == exit_code.SUCCESS.value:
                        f.write(
                            f'<td style="background-color:lightgreen"><div class=scrollable>{value.result}</div></td>')
                    elif value.exit_code == exit_code.ERROR.value:
                        f.write(
                            f'<td style="background-color:lightcoral"><div class=scrollable>{value.result}</div></td>')
                    elif value.exit_code == exit_code.NOT_ATTEMPTED.value:
                        f.write(
                            f'<td style="background-color:lightyellow"><div class=scrollable>{value.result}</div></td>')
                else:
                    f.write(f'<td>{value}</td>')
            f.write('</tr>\n')
        f.write('</table></body></html>')


def extract_student_zips():
    all_subpaths = listdir('.')
    for subpath in all_subpaths:
        print(subpath)
        if not subpath[0].isnumeric():
            continue

        person_name = subpath.split('-')[2].strip()
        person_name = person_name.split(' ')[1] + ', ' + person_name.split(' ')[0]
        print(person_name)

        if not p.exists(person_name):
            makedirs(person_name)

        folder = ''.join(subpath.split('-')[:-1]).strip()

        if subpath[-4:] == ".zip":
            with zipfile.ZipFile(subpath, 'r') as zip_ref:
                zip_ref.extractall(f"{person_name}/{folder}")
            remove(subpath)
        else:
            # 189812-587374 - Andrew Mee- Feb 15, 2023 741 PM - amee_1.cpp
            # cutting the file name off the brightspace generation to group files based time submitted

            if not p.exists(f"{person_name}/{folder}"):
                makedirs(f"{person_name}/{folder}")
            rename(subpath, f"{person_name}/{folder}/{subpath}")


def recursively_extract_zips():
    # recursively extract all zips in the current directory
    all_subpaths = listdir('.')
    for spath in all_subpaths:
        # mac leaves this random folder full of propritary  files
        if spath == '__MACOSX':
            continue
        print(spath)
        if spath[-4:] == ".zip":
            with zipfile.ZipFile(spath, 'r') as zip_ref:
                zip_ref.extractall(f"{spath[:-4]}")
            remove(spath)
        else:
            if p.isdir(spath):
                chdir(spath)
                recursively_extract_zips()
                chdir('..')


def remove_old_submissions():
    all_subpaths = listdir('.')

    for spath in all_subpaths:

        # prevents reruns deleting files
        if p.isfile(f"{spath}/.latest"):
            continue

        if ',' not in spath:
            continue

        folders = listdir(spath)

        with open(f"{spath}/.latest", 'w') as f:
            f.write('')

        most_recent_folder = get_most_recent_path(folders)
        for folder in folders:
            if folder != most_recent_folder:
                shutil.rmtree(f"{spath}/{folder}")


def find_file_path(file_name, cwd=os.getcwd()):
    for root, dirs, files in os.walk(cwd):

        if file_name in files:
            return os.path.join(root, file_name)

        for f in files:
            if f.split('-')[-1].strip() == file_name:
                return os.path.join(root, f)


def get_zips_in_dir():
    all_subpaths = listdir('.')
    zips = []
    for spath in all_subpaths:
        if spath[-4:] == ".zip":
            zips.append(spath)
    return zips


def kill_running_processes(to_kill: list[str]):
    if not to_kill:
        return
    unique_processes = list(set(to_kill))
    unique_processes = [os.path.basename(p) for p in unique_processes]
    try:
        print(f'Killing processes {unique_processes}')
        processes = psutil.process_iter()
        for process in processes:
            try:
                if process.name() in unique_processes or process.name().split('.')[0] in unique_processes:
                    print(f'found {process.name()}')
                    process.terminate()
            except Exception:
                print(f"{traceback.format_exc()}")

    except Exception:
        print(f"{traceback.format_exc()}")


async def async_run_command(command: list[str], cwd: str = os.getcwd()) -> tuple[str, int]:
    # run a command and print the output
    # record the error and return that if there is an error
    try:
        output = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd)
        stdout, stderr = await asyncio.wait_for(output.communicate(), timeout=TIMEOUT)
        # if return code is None, then the process was killed, return error
        if output.returncode is None:
            return f"Process was killed", exit_code.ERROR.value
        elif output.returncode == 0:
            return stdout.decode('utf-8', errors='ignore'), output.returncode
        else:
            return stderr.decode('utf-8', errors='ignore'), output.returncode
    except subprocess.CalledProcessError as e:
        # get the error message
        return f"Exception err={e.stderr.decode('utf-8',errors='ignore')}\n out={e.stdout.decode('utf-8',errors='ignore')}", e.returncode
    except asyncio.TimeoutError:
        GLOBAL_CLEANUP.append(command[0])
        return f"Timeout after {TIMEOUT} seconds", exit_code.ERROR.value


async def run_test(test_case: test_result, command: list[str], cwd: str = os.getcwd()) -> int:
    test_case.result, test_case.exit_code = await async_run_command(command, cwd)
    return test_case.exit_code


async def async_broker(function: Callable) -> list:
    results = []
    counter = 0
    student_dirs = [student for student in listdir('.') if p.isdir(student)]
    # below is for testing
    # student_dirs = [student_dirs[29]]
    # print(student_dirs)
    student_tasks = [function(student) for student in student_dirs]
    print_progress_bar(0, len(student_dirs), prefix='Progress:', suffix='Complete')
    while student_tasks:
        finished, unfinished = await asyncio.wait(student_tasks, return_when=asyncio.FIRST_COMPLETED)
        counter += len(finished)
        print_progress_bar(counter, len(student_dirs), prefix='Progress:', suffix='Complete')
        student_tasks = unfinished
        for task in finished:
            results.append(task.result())
    return results


def grade_all_students(function: Callable) -> list:
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(async_broker(function))
    kill_running_processes(GLOBAL_CLEANUP)
    GLOBAL_CLEANUP.clear()
    return results


async def grade_part_1(student: str) -> part1:

    student_results = part1(student)

    part1_path = os.path.join(os.getcwd(), student, 'part1')
    test_files_folder = os.path.join(os.getcwd(), os.pardir, 'Project1_Grading_S2022', 'allFile2StudentFolder')

    if os.path.exists(part1_path):
        shutil.rmtree(part1_path)

    shutil.copytree(test_files_folder, part1_path)

    rsa_path = find_file_path('rsa435.cc', student)

    if not rsa_path:
        student_results.rsa_file_found.exit_code = 1
        return student_results
    else:
        student_results.rsa_file_found.exit_code = 0

    # copy students rsa435.cc into the folder
    shutil.copy(rsa_path, part1_path)
    # make all

    # run make all and check for errors
    if await run_test(student_results.rsa_file_compiles, ['make', 'all'], part1_path) != 0:
        return student_results

    # run .\rsa435.exe

    binary_path = os.path.join(part1_path, 'rsa435')
    if await run_test(student_results.rsa_file_runs, [binary_path], part1_path) != 0:
        return student_results

    # check for e_n.txt, d_n.txt p_q.txt
    files = ['e_n.txt', 'd_n.txt', 'p_q.txt']
    absolute_files = [os.path.join(part1_path, file) for file in files]

    if not any([os.path.exists(file) for file in absolute_files]):
        student_results.keys_file_found.exit_code = 1
        return student_results
    else:
        student_results.keys_file_found.exit_code = 0

    # make gradeing
    if await run_test(student_results.grading_builds, ['make', 'grading'], part1_path) != 0:
        return student_results

    # run .\RSAPartIGrading -- get output
    binary_path = os.path.join(part1_path, 'RSAPartIGrading')
    if await run_test(student_results.grading_runs, [binary_path], part1_path) != 0:
        return student_results
    else:
        student_results.grading_runs.result = f"{student_results.grading_runs.result.count('pass')}:6\n{student_results.grading_runs.result}"

    return student_results


async def grade_part_2(student: str) -> part2:

    student_results = part2(student)

    part2_path = os.path.join(os.getcwd(), student, 'part2')
    test_files_folder = os.path.join(os.getcwd(), os.pardir, 'Project1_Grading_S2022', 'allFile2StudentFolder - copy')
    key_files_folder = os.path.join(os.getcwd(), os.pardir, 'Project1_Grading_S2022', '435WorkingKeys')

    if os.path.exists(part2_path):
        shutil.rmtree(part2_path)

    shutil.copytree(test_files_folder, part2_path, dirs_exist_ok=True)
    shutil.copytree(key_files_folder, part2_path, dirs_exist_ok=True)

    message_path = find_file_path('messageDigest435.cpp', student)

    if not message_path:
        student_results.message_file_found.exit_code = 1
        return student_results
    else:
        student_results.message_file_found.exit_code = 0

        # copy students rsa435.cc into the folder
    shutil.copy(message_path, part2_path)

    # run make all and check for errors
    if await run_test(student_results.message_file_compiles, ['make', 'digest'], part2_path) != 0:
        return student_results

    test_files = ['one_line.txt', 'two_line.txt', 'bible_part1.txt']
    binary_path = os.path.join(part2_path, 'RSAPart2Grading')
    sign_tasks = []
    verify_tasks = []
    for file in test_files:
        sign_tasks.append(
            asyncio.create_task(
                run_test(student_results[f'{file[:-4]}_signed'],
                         [binary_path, 's', os.path.join(part2_path, file)],
                         part2_path)))
        verify_tasks.append(asyncio.create_task(
            run_test(
                student_results[f'{file[:-4]}_verified'],
                [binary_path, 'v', os.path.join(part2_path, file), os.path.join(part2_path, f'{file}.signature')],
                part2_path)))

    # run sign tasks
    await asyncio.gather(*sign_tasks)

    # run verify tasks
    await asyncio.gather(*verify_tasks)

    return student_results


def get_assignment_name(zip_path: str) -> str:
    if zip_path[0] == 'A' or zip_path[0] == 'P':
        assignment_name = zip_path.split(' ')[0]
    else:
        words = zip_path.split(' ')
        assignment_name = "{} {}".format(words[1], words[2])
    return assignment_name


def unzip_assignment(zip_path: str):
    # unzip the assignment
    assignment_name = get_assignment_name(zip_path)

    if p.exists(assignment_name):
        raise Exception(f"{assignment_name} already exists")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(f"{assignment_name}")
    # if zips folder doesn't exist then make it
    if not p.exists("zips"):
        makedirs("zips")
    # shutil.move(path, f"zips/{path}")
    chdir(assignment_name)
    extract_student_zips()
    recursively_extract_zips()
    chdir('..')


if __name__ == "__main__":
    '''
        Arguments:
        -f or -force: remove and rewrite the unzipped files
        -unzip: unzip all the zips in the current directory
        -p1: grade part 1
        -p2: grade part 2
    '''
    start_dir = getcwd()
    force = False

    # sys.argv.append('-force')
    # sys.argv.append('-unzip')
    # sys.argv.append('-p1')
    sys.argv.append('-p2')

    if len(sys.argv) == 1:
        print("Please specify an argument")
        print("-unzip: unzip assignments in the current directory")
        print("-p1: grade part 1")
        print("-p2: grade part 2")
        exit(1)

    if '-force' in sys.argv or '-f' in sys.argv:
        force = True

    if '-unzip' in sys.argv:
        zips = get_zips_in_dir()
        print("enter a number to unzip a specific zip")
        for i, zip in enumerate(zips):
            print(f"{i}: {zip}")
        print(f"{len(zips)}: all")
        choice = input("Enter a number: ")
        if choice == str(len(zips)):
            for zip in zips:
                if force:
                    shutil.rmtree(get_assignment_name(zip))
                unzip_assignment(zip)
        else:
            if force:
                shutil.rmtree(get_assignment_name(zips[int(choice)]))
            unzip_assignment(zips[int(choice)])

    if '-p1' in sys.argv or '-p2' in sys.argv:
        dirs = listdir('.')
        dirs = [dir for dir in dirs if p.isdir(dir)]
        print("Pick a directory to grade")
        for i, dir in enumerate(dirs):
            print(f"{i}: {dir}")
        choice = input("Enter a number: ")
        chdir(dirs[int(choice)])

    if '-p1' in sys.argv:

        remove_old_submissions()
        now = datetime.datetime.now()
        results = grade_all_students(grade_part_1)
        print(f"Time to grade: {(datetime.datetime.now() - now).total_seconds():.2f}s")
        to_html(results, 'part1.html')

    if '-p2' in sys.argv:
        remove_old_submissions()
        now = datetime.datetime.now()
        results = grade_all_students(grade_part_2)
        print(f"Time to grade: {(datetime.datetime.now() - now).total_seconds():.2f}s")
        to_html(results, 'part2.html')
