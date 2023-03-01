from common_datamodels import run_result, build_result
from workers import run_test
from file_formatter import find_files_by_extension
import os
import shutil

COMPILER = 'g++'
BUILD_ARGS = ['-std=c++11', '-Wall', '-Wextra', '-Werror', '-pedantic', ]
OUTPUT_ARGS = ['-o', '../bin/out']


async def build_test(student: str) -> build_result:
    # build the student's code
    # sort out the paths
    student_results = build_result(student)
    student_path = os.path.join(os.getcwd(), student)
    src_path = os.path.join(student_path, 'src')
    bin_path = os.path.join(student_path, 'bin')
    if not os.path.exists(src_path):
        os.mkdir(src_path)
    if not os.path.exists(bin_path):
        os.mkdir(bin_path)

    # remove any old files in the src and bin folders
    for file in os.listdir(src_path):
        os.remove(os.path.join(src_path, file))
    for file in os.listdir(bin_path):
        os.remove(os.path.join(bin_path, file))

    # find the source files
    src_files = find_files_by_extension('.cpp', student_path)
    src_files.extend(find_files_by_extension('.hpp', student_path))
    src_files.extend(find_files_by_extension('.h', student_path))

    # if no source files, return error
    if not src_files:
        student_results.src_files_found.exit_code = 1
        return student_results
    else:
        student_results.src_files_found.exit_code = 0

    # copy source files to src folder
    for file_path in src_files:
        file_name = os.path.basename(file_path)
        dest_file_path = os.path.join(src_path, file_name)
        if not os.path.exists(dest_file_path):
            shutil.copy2(file_path, src_path)

    # run compiler and specify exact files per student
    # without this, the compiler will use all .cpp files in the directory
    # all the students files get put in the same temp directory during g++ compiliation
    compile_command = [COMPILER, *OUTPUT_ARGS, *src_files]
    #compile_command = [COMPILER, *BUILD_ARGS, *OUTPUT_ARGS, *src_files]

    # run make all
    if await run_test(student_results.build, compile_command, src_path) != 0:
        return student_results

    return student_results
