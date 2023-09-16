import os
from pprint import pprint

sort = {
    1: 'Ukuran',
    2: 'Nama',
}

def scan(dir, res):
    name = os.path.basename(os.path.abspath(dir))
    size_dir = 0
    c_file = 0
    c_folder = 0
    res_r = {
        'files':[],
        'dirs':[]
    }
    res[dir] = {
        'scan': res_r,
        'folderName':name,
        'path': dir,
        'size': 0
        }
    # pprint(res)
    try:
        for path in os.scandir(dir):
            if path.is_file():
                c_file += 1
                size = os.stat(path.path).st_size
                size_dir += size
                res['count'] += 1
                res['total_size'] += size
                tmp = {
                    'name': path.name,
                    'size': size,
                    'path': path.path
                    }
                check_large_file(res['10_largest_files'], tmp)
                res_r['files'].append(tmp)
            elif path.is_dir():
                c_folder += 1
                r = scan(path.path, res)
                size_dir += r[0]
                tmp = {
                    'name': path.name,
                    'path': path.path,
                    'size': r[0],
                    'contains': {
                        'files': r[1],
                        'folders': r[2]
                        }
                    }
                res_r['dirs'].append(tmp)
            else:
                continue
    except PermissionError:
        res_r = {'status':'permision_denied'}
    except FileNotFoundError:
        res_r = {'status':'file_not_found'}
    res[dir]['size'] = sum_size(res_r)
    res[dir]['contains'] = {
                    'files': c_file,
                    'folders': c_folder
                }
    return [size_dir, c_file, c_folder]

def sum_size(data: dict):
    try:
        size = 0
        size += get_size(data['dirs'])
        size += get_size(data['files'])
        return size
    except KeyError:
        if data['status'] == 'permision_denied':
            return None
        elif data['status'] == 'file_not_found':
            return None

def convert_bytes(num: int):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f'{num} {x}' if x == 'bytes' else f'{num:.1f} {x}'
        num /= 1024.0

def get_root_dir(dictionary):
    c = 0
    for key in dictionary:
        c += 1
        if c == 4:
            return dictionary[key]
    raise IndexError

def get_size(subdirs: list):
    size = 0
    for dir in subdirs:
        size += dir['size']
    return size

def print_dir(dir: dict):
    c = 0
    for i in dir['dirs']:
        c += 1
        print(f" {c}. {i['name']}".ljust(50) + 'd'.ljust(4) + convert_bytes(i['size']))
    for i in dir['files']:
        c += 1
        print(f" {c}. {i['name']}".ljust(50) + 'f'.ljust(4) + convert_bytes(i['size']))

def print_bgst(files: list):
    c = 0
    for i in files:
        c+= 1
        print(f" {c}. {i['name']}".ljust(50) + 'f'.ljust(4) + convert_bytes(i['size']))

def change_directory(res: dict, tmp:dict, idx: int):
    temp = tmp['scan']
    pprint(temp)
    ld = len(temp['dirs'])
    lf = len(temp['files'])
    # l = ld + lf
    if idx <= ld:
        return res[temp['dirs'][idx-1]['path']]
    else:
        return tmp


def _size(data: dict):
    return data['size']

def sort_size(dir: dict):
    dir['dirs'].sort(key=_size, reverse=True)
    dir['files'].sort(key=_size, reverse=True)

def _name(data: dict):
    return data['name'].upper()

def sort_name(dir: dict):
    dir['dirs'].sort(key=_name, reverse=False)
    dir['files'].sort(key=_name, reverse=False)

def check_large_file(res: list, file: dict):
    # pprint(res)
    res.sort(key=_size, reverse=True)
    if len(res) < 10:
        res.append(file)
    else:
        for f in res:
            if f['size'] < file['size']:
                print(f"{f['size']} < {file['size']}")
                print(res)
                res.insert(res.index(f), file)
                res.pop()
                break

def tampilkanhasil(res):
    sorting = 2
    disp = []
    stack = []
    temp = get_root_dir(res)
    # pprint(res)
    stack.append(temp['path'])
    while True:
        print_bgst(res['10_largest_files'])
        if sorting == 1:
            sort_size(temp['scan'])
        elif sorting == 2:
            sort_name(temp['scan'])
        for i in stack:
            disp.append(res[i]['folderName'])
        print("================================================================")
        print(f" Found : {temp['contains']['files'] + temp['contains']['folders']}")
        print(f"      File   : {temp['contains']['files']}")
        print(f"      Folder : {temp['contains']['folders']}")
        print(f" Size : {convert_bytes(temp['size'])}")
        print("================================================================")
        print(f" Sort : {sort[sorting]}")
        print("================================================================")
        print_dir(temp['scan'])
        print("================================================================")
        print(" 1. Urutkan berdasarkan Ukuran ")
        print(" 2. Urutkan berdasarkan Nama")
        print(" 0. Back")
        m = input(f"[{'  '.join(disp)}] # ")
        if m.isnumeric():
            if m == '0':
                break
            elif m == '1':
                sorting = 1
            elif m == '2':
                sorting = 2
        else:
            m = m.split(' ')
            if m[0] == 'cd':
                if len(m) == 1:
                    temp = get_root_dir(res)
                    stack.clear()
                    stack.append(temp['path'])
                elif m[1].isnumeric():
                    temp = change_directory(res, temp, int(m[1]))
                    stack.append(temp['path'])
                elif m[1] == '..':
                    if stack[-1] != get_root_dir(res)['path']:
                        stack.pop()
                        prev = stack[-1]
                        temp = res[prev]
        disp.clear()

def run():
    res = {
        'count': 0,
        'total_size': 0,
        '10_largest_files': [],
        }
    while True:
        print(" 1 . Scan")
        print(" 2 . Check Result")
        print(" 0 . Exit")
        m = int(input("Menu : "))
        if m == 1:
            res = {
                'count': 0,
                'total_size': 0,
                '10_largest_files': [],
           }
            dir = input("Enter directory: ")
            scan(dir, res)
        elif m == 2:
            while True:
                print("================================================================")
                print(f"File ditemukan : {res['count']}")
                print(f"Total size scanned : {convert_bytes(res['total_size'])}")
                print("================================================================")
                print(" 1. Tampilkan Hasil")
                print(" 0. Back")
                # pprint(res)
                p = int(input("Pilih : "))
                if p == 0:
                    break
                elif p == 1:
                    tampilkanhasil(res)
        elif m == 0:
            break

if __name__ == '__main__':
    run()