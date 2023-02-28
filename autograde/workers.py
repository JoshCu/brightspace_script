import traceback
import asyncio
import os
import psutil

from typing import Callable

from common_datamodels import test_result, exit_code
from render import print_progress_bar

# timeout in seconds for each test
TIMEOUT = 5*60

GLOBAL_CLEANUP = []


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
            return stderr.decode(
                'utf-8', errors='ignore') + '\nERROR\n' + stdout.decode(
                'utf-8', errors='ignore'), output.returncode
    except asyncio.CalledProcessError as e:
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
    student_dirs = [student for student in os.listdir('.') if os.path.isdir(student)]
    # below is for testing
    # student_dirs = [student_dirs[1]]
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
