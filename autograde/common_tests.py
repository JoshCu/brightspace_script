from common_datamodels import run_result, build_result
from workers import run_test
from file_formatter import find_files_by_extension
import os
import shutil

COMPILER = 'g++'
BUILD_ARGS = ['-std=c++11', '-Wall', '-Wextra', '-Werror', '-pedantic', ]
OUTPUT_ARGS = ['-o', '../bin/out', '*.cpp']
#BUILD_COMMAND = [COMPILER, *BUILD_ARGS, *OUTPUT_ARGS]
BUILD_COMMAND = [COMPILER, *OUTPUT_ARGS]


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

    # find the source files
    src_files = find_files_by_extension('.cpp', student_path)
    src_files.extend(find_files_by_extension('.hpp', student_path))

    # if no source files, return error
    if not src_files:
        student_results.src_files_found.exit_code = 1
        return student_results
    else:
        student_results.src_files_found.exit_code = 0

    # copy source files to src folder
    for file in src_files:
        shutil.copy(file, src_path)

    # run make all
    if await run_test(student_results.build, BUILD_COMMAND, src_path) != 0:
        return student_results

    return student_results


# async def run_test(student: str) -> run_result:
#     try:
#         test.result = await run_command(args, path)
#         test.exit_code = 0
#         return 0
#     except Exception as e:
#         test.result = str(e)
#         test.exit_code = 1
#         return 1
