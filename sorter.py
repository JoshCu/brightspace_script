from os import listdir, makedirs, rename, remove, chdir, getcwd
from os import path as p
from shutil import move
import zipfile

import os
import sys
import subprocess
import datetime

# give either full path to compiler or just the name of the compiler
# if just the name of the compiler, it will assume it is in the path
COMPILER = "g++"
COMPILER_FLAGS = ""
# only reports failures
HIDE_SUCCESS = False


def extract_date(path):
    # get the date from the path
    # convert it into a datetime object
    # return the datetime object
    date_string = path.split('-')[3].strip()
    # formatted as Jan 1, 2023 1114 AM

    # manually day and pad the hour but not minutes
    # jfc what is this format brightspace
    month = date_string.split()[0]
    year = date_string.split()[2]
    day = date_string.split()[1][:-1]
    hour = date_string.split()[3][:-2]
    minute = date_string.split()[3][-len(hour):]
    AmPm = date_string.split()[4]

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
        date = extract_date(path)
        if most_recent_date is None or date > most_recent_date:
            most_recent = path
            most_recent_date = date

    return most_recent


def find_main_cpp(path):
    if os.path.isfile(path):
        if path.endswith(".cpp"):
            return os.path.join(os.getcwd(), path)
        else:
            return None
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".cpp"):
                    return (os.path.join(root, file))


def to_csv(results):
    # write the results to a csv file
    # convert results to a grid on a webpage
    # if success then make the cell green
    # if failure then make the cell red
    # add border to the table
    with open("results.html", "w") as f:
        f.write("<table style=\"border: 1px solid black;\">\n")
        for result in results:
            for key in result:
                if result[key] == "SUCCESS":
                    f.write(f"<tr><td>{key}</td><td style=\"background-color: green;\">{result[key]}</td></tr>\n")
                else:
                    f.write(f"<tr><td>{key}</td><td style=\"background-color: red;\">{result[key]}</td></tr>\n")
        f.write("</table>\n")

    with open("results.csv", "w") as f:
        for result in results:
            for key in result:
                f.write(f"{key} : {result[key]}\n")


def compile_all():
    results = []
    # get all the directories in the current directory
    all_paths = os.listdir(os.getcwd())
    original_path = os.getcwd()
    # go into each students directory
    for path in all_paths:
        if os.path.isfile(os.path.join(original_path, path)):
            continue

        name = path
        os.chdir(original_path)
        os.chdir(path)
        # find the most recent main.cpp
        most_recent = get_most_recent_path(os.listdir(os.getcwd()))
        main_path = find_main_cpp(most_recent)

        result = {}
        if main_path is None:
            result[name] = "ERROR No .cpp file found"
            continue
        else:
            # compile the main.cpp and report errors
            try:
                if COMPILER_FLAGS == "":
                    subprocess.run([COMPILER, main_path], check=True, capture_output=True)
                else:
                    subprocess.run([COMPILER, COMPILER_FLAGS, main_path], check=True, capture_output=True)
                result[name] = "SUCCESS"
                os.remove("a.exe")
            except subprocess.CalledProcessError as e:
                # get the error message
                result[name] = f"Compilation failed Exception err={e.stderr}\n out={e.stdout}"

        results.append(result)

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
            #move(path, f"zips/{path}")
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
