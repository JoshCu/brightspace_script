from datetime import datetime
import os
import shutil
import zipfile

from render import print_progress_bar


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

    # comma omitted as we don't re add it after it's os.removed
    dt = datetime.strptime(new_date_string, "%b %d %Y %I %M %p")
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


def extract_student_zips():
    all_subpaths = os.listdir('.')
    print_progress_bar(0, len(all_subpaths), prefix='Progress:', suffix='Complete')
    for i, subpath in enumerate(all_subpaths):
        print_progress_bar(i + 1, len(all_subpaths), prefix='Progress:', suffix='Complete')

        if not subpath[0].isnumeric():
            continue

        person_name = subpath.split('-')[2].strip()
        person_name = person_name.split(' ')[1] + ', ' + person_name.split(' ')[0]

        if not os.path.exists(person_name):
            os.makedirs(person_name)

        folder = ''.join(subpath.split('-')[:-1]).strip()
        file = subpath.split('-')[-1].strip()

        if subpath[-4:] == ".zip":
            if not os.path.exists(f"{person_name}/{folder}"):
                os.makedirs(f"{person_name}/{folder}")
            with zipfile.ZipFile(subpath, 'r') as zip_ref:
                zip_ref.extractall(f"{person_name}/{folder}")
            os.remove(subpath)
        else:
            # 189812-587374 - Andrew Mee- Feb 15, 2023 741 PM - amee_1.cpp
            # cutting the file name off the brightspace generation to group files based time submitted

            if not os.path.exists(f"{person_name}/{folder}"):
                os.makedirs(f"{person_name}/{folder}")
            os.rename(subpath, f"{person_name}/{folder}/{file}")


def recursively_extract_zips():
    # recursively extract all zips in the current directory
    all_subpaths = os.listdir('.')
    for spath in all_subpaths:
        # mac leaves this random folder full of propritary  files
        if spath == '__MACOSX':
            continue

        if spath[-4:] == ".zip" and not os.path.isdir(spath):
            with zipfile.ZipFile(spath, 'r') as zip_ref:
                zip_ref.extractall(f"{spath[:-4]}")
            os.remove(spath)
        else:
            if os.path.isdir(spath):
                os.chdir(spath)
                recursively_extract_zips()
                os.chdir('..')


def remove_old_submissions():
    all_subpaths = os.listdir('.')

    for spath in all_subpaths:

        # prevents reruns deleting files
        if os.path.isfile(f"{spath}/.latest"):
            continue

        if ',' not in spath:
            continue

        folders = os.listdir(spath)
        folders = [f for f in folders if os.path.isdir(f"{spath}/{f}")]

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


def find_files_by_extension(file_extension: str, cwd=os.getcwd()) -> list[str]:
    if file_extension[0] == '.':
        file_extension = file_extension[1:]
    all_paths = []
    for root, dirs, files in os.walk(cwd):
        if '__MACOSX' in root:
            continue
        for f in files:
            if f.split('.')[-1] == file_extension:
                all_paths.append(os.path.join(root, f))
    return all_paths


def get_zips_in_dir():
    all_subpaths = os.listdir('.')
    zips = []
    for spath in all_subpaths:
        if spath[-4:] == ".zip":
            zips.append(spath)
    return zips


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

    if os.path.exists(assignment_name):
        raise Exception(f"{assignment_name} already exists")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(f"{assignment_name}")
    # if zips folder doesn't exist then make it
    if not os.path.exists("zips"):
        os.makedirs("zips")
    # shutil.move(path, f"zips/{path}")
    os.chdir(assignment_name)
    extract_student_zips()
    recursively_extract_zips()
    os.chdir('..')
