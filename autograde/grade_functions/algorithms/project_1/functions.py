import asyncio
import os
import shutil
import subprocess

from datamodels import part1, part2
from autograde.common_datamodels import test_result
from autograde.file_formatter import find_file_path
from autograde.workers import run_test


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
    test_files_folder = os.path.join(os.getcwd(), os.pardir, 'Project1_Grading_S2022', 'allFile2StudentFolder')
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

    # copy students messageDigest435.cpp into the folder
    shutil.copy(message_path, part2_path)

    # run make all and check for errors
    if await run_test(student_results.message_file_compiles, ['make', 'digest'], part2_path) != 0:
        return student_results

    if await run_test(test_result(), ['make', 'grading'], part2_path) != 0:
        return student_results

    test_files = ['one_line.txt', 'two_lines.txt', 'bible_part1.txt']
    binary_path = os.path.join(part2_path, 'RSAPart2Grading')
    sign_tasks = []
    verify_tasks = []
    for file in test_files:
        sign_tasks.append(
            asyncio.create_task(
                run_test(student_results[f'{file[:-4]}_signed'],
                         [binary_path, 's', os.path.join(part2_path, file)],
                         part2_path)))

    old_files = set(os.listdir(part2_path))
    # run sign tasks
    await asyncio.gather(*sign_tasks)
    new_files = set(os.listdir(part2_path)) - old_files

    with open(os.path.join(part2_path, 'modified.txt'), 'w') as f:
        f.write("modified file test")

    if len(new_files) == 0:
        return student_results

    # some students append .signature, some .signed, just get it straight from the files
    signature_appenddix = None
    signed_files = set()
    for file in new_files:
        if file.split('.')[-1].lower().startswith('sig'):
            signature_appenddix = file.split('.')[-1]
            signed_files.add(file)

    if not signature_appenddix:
        return student_results

    for file in test_files:
        verify_tasks.append(
            asyncio.create_task(
                run_test(
                    student_results[f'{file[:-4]}_verified'],
                    [binary_path, 'v', os.path.join(part2_path, file),
                     os.path.join(part2_path, f'{os.path.join(part2_path, file)}.{signature_appenddix}')],
                    part2_path)))
        verify_tasks.append(
            asyncio.create_task(
                run_test(
                    student_results[f'{file[:-4]}_modified'],
                    [binary_path, 'v', os.path.join(part2_path, "modified.txt"),
                     os.path.join(part2_path, f'{os.path.join(part2_path, file)}.{signature_appenddix}')],
                    part2_path)))
    signed_file_original_names = ['.'.join(file.split('.')[:-1]) for file in signed_files]
    # students return codes are not consistent, so check if the file was signed
    # if not, set the exit code to 1
    for file in test_files:
        if file not in signed_file_original_names:
            student_results[f'{file[:-4]}_signed'].exit_code = 1
            student_results[f'{file[:-4]}_verified'].exit_code = 1
            student_results[f'{file[:-4]}_modified'].exit_code = 1

    # run verify tasks
    await asyncio.gather(*verify_tasks)

    return student_results
