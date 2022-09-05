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
    compress_file_ext = ('7z', 'zip', 'rar', 'tar.gz', 'tar', 'tgz', '001')
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

    opts, args = getopt(sys.argv[1:], 'ud:', ['update', "dir="])
    for opt_name, opt_value in opts:
        if opt_name in ('-u', '--update'):
            get_output(
                "wget https://github.com/kaiwu-astro/garage/raw/main/auto7z.py -O auto7z.py")
            urllib.request.urlretrieve(
                "https://github.com/kaiwu-astro/garage/raw/main/auto7z.py", my_dir+os.sep+"auto7z.py")
            os.chmod("auto7z.py", 0o755)
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
                    cmd = f"cd {os.getcwd()}; 7z x '{fn}' -p'{pwd}' -r -aoa -o'{os.path.splitext(fn)[0]}'"
                    poolres.append(p.apply_async(get_output, args=(cmd,)))
                p.close()
                outputs = [''.join(r.get()) for r in poolres]
                p.join()
            need_new_pwd = False if "Everything is Ok" in ''.join(outputs) else True
            
            # # 单线程
            # need_new_pwd = True
            # for ipwdtry, pwdp1 in enumerate(passwords):
            #     sys.stdout.write(
            #         f"\rTrying password {ipwdtry+1} / {len(passwords)}")
            #     sys.stdout.flush()
            #     pwd = pwdp1[:-1]
            #     cmd = f"cd {os.getcwd()}; 7z x '{fn}' -p'{pwd}' -r -aoa -o'{os.path.splitext(fn)[0]}'"
            #     # print(cmd)
            #     output = get_output(cmd)
            #     if "Everything is Ok" in ''.join(output):
            #         need_new_pwd = False
            #         break
            output = ''
            if need_new_pwd:
                while not "Everything is Ok" in ''.join(output):
                    pwd = input("\nEnter password: ")
                    cmd = f"cd {os.getcwd()}; 7z x '{fn}' -p'{pwd}' -r -aoa -o'{os.path.splitext(fn)[0]}'"
                    print(cmd)
                    output = get_output(cmd)
                    print("\n".join(output))
                passwords.append(pwd + '\n')
            os.rename(fn, "extracted" + os.sep +fn)

            nfile = 0
            for root_dir, cur_dir, files in os.walk(os.path.splitext(fn)[0]):
                nfile += len(files)
            
            if nfile <= 5:
                for root_dir, cur_dir, files in os.walk(os.path.splitext(fn)[0], topdown=False):
                    for _f in files:
                        os.rename(root_dir + os.sep + _f,
                                  os.getcwd() + os.sep + _f)
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


