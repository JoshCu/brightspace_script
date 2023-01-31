from ctypes import sizeof
from os import listdir, makedirs, rename, remove, chdir, getcwd
from os import path as p
import shutil
import zipfile

import os
import sys
import subprocess
import datetime

# give either full path to compiler or just the name of the compiler
# if just the name of the compiler, it will assume it is in the path
COMPILER = "g++"
COMPILER_FLAGS = []
# only reports failures
HIDE_SUCCESS = False


def find_AM_PM(path):
    # find the AM or PM in the path
    # if it is not found then return None
    # otherwise return the index of the AM or PM
    if "AM" in path:
        return path.index("AM")
    elif "PM" in path:
        return path.index("PM")
    else:
        return None


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
        if path in ["src", "bin"]:
            continue
        date = extract_date(path)
        if most_recent_date is None or date > most_recent_date:
            most_recent = path
            most_recent_date = date

    return most_recent


def get_most_recent_file(filename, student_path):
    # get the most recent path
    pass
    most_recent = None
    most_recent_date = None

    student_files = os.listdir(student_path)

    for path in student_files:
        if path in ["src", "bin"]:
            continue
        if filename in path:
            date = extract_date(path)
            if most_recent_date is None or date > most_recent_date:
                most_recent = path
                most_recent_date = date

    return most_recent


# def find_main_cpp(path):
#     if os.path.isfile(path):
#         if path.endswith(".cpp"):
#             return os.path.join(os.getcwd(), path)
#         else:
#             return None
#     elif os.path.isdir(path):
#         for root, dirs, files in os.walk(path):
#             for file in files:
#                 if file.endswith(".cpp"):
#                     return (os.path.join(root, file))

def rename_files(student_path):
    # get the names of all the files in the path
    # get the most recent version, and copy it to src
    file_names = []
    for file in os.listdir(student_path):
        # assuming the file names don't have spaces in them
        name = file.split(' ')[-1]
        file_names.append(name)

    #  remove duplicates
    file_names = list(set(file_names))

    for file in file_names:
        most_recent = get_most_recent_file(file, student_path)
        if most_recent is not None:
            shutil.copy(most_recent, os.path.join(student_path, "src", file))


def to_csv(results):
    # write the results to a csv file
    # convert results to a grid on a webpage
    # if success then make the cell green
    # if failure then make the cell red
    # add border to the table
    with open("results.csv", "w") as f:
        for student in sorted(results.keys()):
            f.write(str(student) + ",")
            for result in results[student]:
                f.write(str(result[1]) + ",")
            f.write("\n")

    with open("results.html", "w") as f:
        f.write("<table border=\"1\">")
        for student in sorted(results.keys()):
            f.write("<tr>")
            f.write("<td>" + student + "</td>")
            for result in results[student]:
                if str(result[0]) == "Compilation":
                    if str(result[1]) == "SUCCESS":
                        f.write("<td bgcolor=\"green\">" + str(result[1]) + "</td>")
                    else:
                        f.write("<td bgcolor=\"red\">" + str(result[1]) + "</td>")
                elif str(result[0]) == "Mixed Files":
                    if str(result[1]) == "True":
                        f.write("<td bgcolor=\"blue\">" + str(result[1]) + "</td>")
                    else:
                        f.write("<td bgcolor=\"white\">" + str(result[1]) + "</td>")
            f.write("</tr>")
        f.write("</table>")


def compile_all():
    results = {}
    # get all the directories in the current directory
    all_paths = os.listdir(os.getcwd())
    original_path = os.getcwd()
    # go into each students directory
    for path in all_paths:
        if os.path.isfile(os.path.join(original_path, path)):
            continue
        result = []
        name = path
        os.chdir(original_path)
        os.chdir(path)

        # check to see if there is a mix of files and directories
        files_present, directories_present = False, False
        for file in os.listdir(os.getcwd()):
            if os.path.isfile(file):
                files_present = True
            if os.path.isdir(file):
                directories_present = True

        result.append(("Mixed Files", files_present and directories_present))

        # create a src directory if it doesn't exist
        if "src" not in os.listdir(os.getcwd()):
            os.mkdir("src")

        # create a bin directory if it doesn't exist
        if "bin" not in os.listdir(os.getcwd()):
            os.mkdir("bin")

        # find the most recent main.cpp
        most_recent = get_most_recent_path(os.listdir(os.getcwd()))

        if os.path.isdir(most_recent):
            # copy all files into src
            for root, dirs, files in os.walk(most_recent):
                for file in files:
                    shutil.copy(os.path.join(root, file), os.path.join(os.getcwd(), "src", file))
        else:
            # we need to copy the files and rename them so imports work
            rename_files(os.getcwd())

        src_path = os.path.join(os.getcwd(), "src")

        os.chdir(src_path)

        # compile the main.cpp and report errors
        try:
            print("Current WD:")
            print(os.getcwd())
            src_path = os.path.join(original_path, path, "src", "*.cpp")
            binary_path = os.path.join(original_path, path, "bin", "out.exe")
            if len(COMPILER_FLAGS) == 0:
                p = subprocess.Popen(f'{COMPILER} *.cpp' + " -o " + f'"{binary_path}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                if(len(err) > 0):
                    result.append(("Compilation", "Compilation failed: " + str(err)))
                else:
                    result.append(("Compilation", "SUCCESS"))
                #subprocess.run([COMPILER, os.path.join(original_path, path, "src", "*.cpp"), "-o", binary_path], check=True, capture_output=True, shell=True)
            else:
                subprocess.run(
                        [COMPILER, *COMPILER_FLAGS, os.path.join(original_path, path, "src", "*.cpp"), "-o", binary_path],
                   check=True, capture_output=True, shell=True)
            #result.append(("Compilation", "SUCCESS"))

        except subprocess.CalledProcessError as e:
            # get the error message
            print(e.cmd)
            result.append(("Compilation", f"Compilation failed Exception err={e.stderr}\n out={e.stdout}"))

        results[name] = result

    os.chdir(original_path)
    to_csv(results)

    # write errors to a file


if __name__ == "__main__":

    start_dir = getcwd()

    all_paths = listdir('.')

    for path in all_paths:
        print(path)
        if path[-4:] == ".zip":
            if path[0] == 'A':
                name = path.split(' ')[0]
            else:
                words = path.split(' ')
                name = "{} {}".format(words[1], words[2])
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(f"{name}")
            # if zips folder doesn't exist then make it
            if not p.exists("zips"):
                makedirs("zips")
            #shutil.move(path, f"zips/{path}")
            chdir(name)
            all_subpaths = listdir('.')
            for spath in all_subpaths:
                print(spath)
                if spath[0].isnumeric():
                    person_name = spath.split('-')[2].strip()
                    person_name = person_name.split(' ')[1] + ', ' + person_name.split(' ')[0]
                    print(person_name)
                    if not p.exists(person_name):
                        makedirs(person_name)
                    if spath[-4:] == ".zip":
                        with zipfile.ZipFile(spath, 'r') as zip_ref:
                            zip_ref.extractall(f"{person_name}/{spath}")
                        remove(spath)
                    else:
                        rename(spath, f"{person_name}/{spath}")
            compile_all()
            chdir(start_dir)
