from menu import pick_directory
from comparison import get_all_paths
import shutil
import os

# Creates a folder in the assignemnt directory with each students files in it

if __name__ == '__main__':
    os.chdir('put_zips_here')
    pick_directory()

    dirs = os.listdir('.')
    dirs = [dir for dir in dirs if os.path.isdir(dir)]
    dirs = [dir for dir in dirs if ',' in dir]
    print(f"Checking {len(dirs)} directories")

    if not os.path.isdir('aaa_speed'):
        os.mkdir('aaa_speed')
    else:
        shutil.rmtree('aaa_speed')
        os.mkdir('aaa_speed')

    paths = get_all_paths('.cpp', dirs)
    for path in paths:
        student_name = path.split(os.path.sep)[0]
        shutil.copy(path, f'aaa_speed/{student_name}-{os.path.basename(path)}')
