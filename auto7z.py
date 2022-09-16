#!/usr/bin/env python3
import os
import sys
import stat
import shutil
import signal
import urllib.request
from subprocess import run
from glob import glob
from multiprocessing import Pool
from getopt import gnu_getopt as getopt


def get_output(cmd: str, raise_error=False) -> list:
    '''
    get output of a shell cmd. ignore error by default
    return: list of strings (one line per item, no \\n in the end)
    '''
    return str(run(cmd, shell=True, check=raise_error, capture_output=True).stdout, encoding='utf-8').split("\n")[:-1]


def update_toUnzipList():
    compress_file_ext = ('7z', 'zip', 'rar', 'tar.gz', 'tar', 'tgz', '001', '002', '003', '004', '005', '006', '007', '008', '009', '010', '011', '012', '013', '014', '015', '016', '017', '018', '019', '020')
    fl = os.listdir()
    to_unzip = []
    for fn in fl:
        if not os.path.isdir(fn):
            if os.path.splitext(fn)[-1][1:] in compress_file_ext:
                to_unzip.append(fn)
    return to_unzip


def is_7z_exist():
    if not "Copyright" in "".join(get_output("7z --help")):
        return False
    else:
        return True


def move_if_in_sandboxie(zip_file_dir, to_unzip, moveto='F:\\Download\\'):
    if 'sandboxie' in zip_file_dir.lower() or 'defaultbox' in zip_file_dir.lower():
        for fn in to_unzip:
            shutil.move(fn, moveto + os.sep + fn)
        os.chdir(moveto)
        zip_file_dir = moveto
        to_unzip = update_toUnzipList()
    return zip_file_dir, to_unzip


if __name__ == "__main__":
    my_dir = os.path.abspath(os.path.dirname(__file__))
    passwordfile = my_dir + os.sep + "passwords.txt"
    zip_file_dir = my_dir
    prefix7z = 'wsl ' if os.sep == '\\' else ""

    opts, args = getopt(sys.argv[1:], 'ud:', ['update', "dir="])
    for opt_name, opt_value in opts:
        if opt_name in ('-u', '--update'):
            get_output(
                f"wget https://github.com/kaiwu-astro/garage/raw/main/auto7z.py -O {my_dir}{os.sep}auto7z.py")
            urllib.request.urlretrieve(
                "https://github.com/kaiwu-astro/garage/raw/main/auto7z.py", my_dir+os.sep+"auto7z.py")
            os.chmod(my_dir+os.sep+"auto7z.py", 0o755)
            print("Upgraded.")
            sys.exit(0)
        if opt_name in ('-d', '--dir'):
            zip_file_dir = opt_value

    if not is_7z_exist():
        raise OSError("7z program does not exist.")

    if not os.path.isfile(passwordfile):
        with open(passwordfile, 'w', encoding='utf-8') as f:
           f.write("\n")

    # print(get_output("cat passwords.txt"))
    with open(passwordfile, 'r', encoding='utf-8') as f:
       passwords = f.readlines()

    os.chdir(zip_file_dir)

    nExtracted = 0
    to_unzip = update_toUnzipList()
    zip_file_dir, to_unzip = move_if_in_sandboxie(zip_file_dir, to_unzip)
    total_nToUnzip = 0
    if not os.path.isdir("extracted"):
       os.mkdir("extracted")

    while len(to_unzip) != 0:
        total_nToUnzip += len(to_unzip)
        for fn in to_unzip:
            print(f"{nExtracted+1}/{total_nToUnzip}\t{fn}")
            if not os.path.isfile(fn):
                print(f"{fn} was removed.")
                continue
            # 多线程
            def pool_exit(signum, frame):
                try:
                    p.terminate()
                except:
                    pass
                sys.exit(0)
            signal.signal(signal.SIGTERM, pool_exit)
            with Pool(processes=5) as p:
                poolres = []
                for ipwdtry, pwdp1 in enumerate(passwords):
                    sys.stdout.write(
                        f"\rTrying password {ipwdtry+1} / {len(passwords)}")
                    sys.stdout.flush()
                    pwd = pwdp1[:-1]
                    cmd = f"cd {os.getcwd()}; {prefix7z} 7z x '{fn}' -p'{pwd}' -r -aoa -o'{os.path.splitext(fn)[0]}'"
                    poolres.append(p.apply_async(get_output, args=(cmd,)))
                p.close()
                outputs = [''.join(r.get()) for r in poolres]
                p.join()
            need_new_pwd = False if "Everything is Ok" in ''.join(outputs) else True
            
            output = ''
            if need_new_pwd:
                while not "Everything is Ok" in ''.join(output):
                    pwd = input("\nEnter password: ")
                    cmd = f"cd {os.getcwd()}; {prefix7z} 7z x '{fn}' -p'{pwd}' -r -aoa -o'{os.path.splitext(fn)[0]}'"
                    print(cmd)
                    output = get_output(cmd)
                    print("\n".join(output))
                passwords.append(pwd + '\n')

            shutil.move(fn, "extracted" + os.sep +fn)
            if fn.endswith(".001"):
                num = 2
                while True:
                    tryfile = fn.replace(".001", f'.00{num}')
                    if tryfile in to_unzip:
                        shutil.move(tryfile, "extracted" + os.sep + tryfile)
                        num += 1
                    else:
                        break

            nfile = 0
            for root_dir, cur_dir, files in os.walk(os.path.splitext(fn)[0]):
                for _f in files:
                    if not "萌次元" in _f and not "喵子" in _f:
                        nfile += 1
            
            if nfile <= 5:
                INTERRUPT_MOVE = False
                for root_dir, cur_dir, files in os.walk(os.path.splitext(fn)[0], topdown=False):
                    for _f in files:
                        if os.path.isfile(os.getcwd() + os.sep + _f) and os.path.getsize(os.getcwd() + os.sep + _f)/1024/1024 > 10 and not "萌次元" in _f and not "喵子" in _f:
                            INTERRUPT_MOVE = True
                            print(f"Files in extracted {fn} cannot be moved to rootdir. 已存在重名文件. ")
                            break
                        shutil.move(root_dir + os.sep + _f,
                                    os.getcwd() + os.sep + _f)
                    if not INTERRUPT_MOVE:
                        os.rmdir(root_dir)
            else:
                first_layer_ndirOrFiles = os.listdir(os.path.splitext(fn)[0])
                if len(first_layer_ndirOrFiles) <= 2:
                    for ford in first_layer_ndirOrFiles:
                        shutil.move(os.path.splitext(fn)[0] + os.sep + ford, ford)
                    os.rmdir(root_dir)

            nExtracted += 1
            print("  Succeeded.")

        to_unzip = update_toUnzipList()

    with open(passwordfile, 'w', encoding='utf-8') as f:
        f.write(''.join(passwords))

    if os.sep == '/':
        print('\n'.join(get_output("df -h `pwd`")))
    else:
        print('\n'.join(get_output(
            "Get-Volume -Driveletter " + zip_file_dir.split(":")[0])))

    print(f"{nExtracted} files extracted.")

    # print(get_output("cat passwords.txt"))


