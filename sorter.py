from os import listdir, makedirs, rename, remove
from os import path as p
import zipfile
all_paths = listdir('.')

for path in all_paths:
    print(path)
    if path[0].isnumeric():
        person_name = path.split('-')[2].strip()
        person_name = person_name.split(' ')[1] + ', ' + person_name.split(' ')[0]
        print(person_name)
        if not p.exists(person_name):
            makedirs(person_name)
        if path[-4:] == ".zip":
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(f"{person_name}/{path}")
            remove(path)
        else:
            rename(path, f"{person_name}/{path}")
        
