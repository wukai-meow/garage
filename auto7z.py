#!/usr/bin/env python3
import os
import sys
from subprocess import run
from glob import glob


def get_output(cmd: str, raise_error=False) -> list:
    '''
    get output of a shell cmd. ignore error by default
    return: list of strings (one line per item, no \\n in the end)
    '''
    return str(run(cmd, shell=True, check=raise_error, capture_output=True).stdout, encoding='utf-8').split("\n")[:-1]


def update_toUnzipList():
    compress_file_ext = ('7z', 'zip', 'rar', 'tar.gz', 'tar', 'tgz')
    fl = os.listdir()
    to_unzip = []
    for fn in fl:
        if os.path.splitext(fn)[-1][1:] in compress_file_ext:
            to_unzip.append(fn)
    return to_unzip


if __name__ == "__main__":
    my_dir = os.path.abspath(os.path.dirname(__file__))
    passwordfile = my_dir + os.sep + "passwords.txt"

    if not os.path.isfile(passwordfile):
        with open(passwordfile, 'w') as f:
           f.write("\n")

    # print(get_output("cat passwords.txt"))
    with open(passwordfile, 'r') as f:
       passwords = f.readlines()

    if not os.path.isdir("extracted"):
       os.mkdir("extracted")

    nExtracted = 0
    to_unzip = update_toUnzipList()
    total_nToUnzip = 0
    while len(to_unzip) != 0:
        total_nToUnzip += len(to_unzip)
        for fn in to_unzip:
            print(f"{nExtracted+1}/{total_nToUnzip}\t{fn}")
            nsavedpwd = len(passwords)
            need_new_pwd = False
            ipwdtry = 0
            output = ''
            while not "Everything is Ok" in ''.join(output):
                if ipwdtry < nsavedpwd:
                    sys.stdout.write("\r")
                    sys.stdout.write(
                        f"Trying password {ipwdtry+1} / {nsavedpwd}")
                    sys.stdout.flush()
                    pwd = passwords[ipwdtry][:-1]
                    cmd = f"7z x '{fn}' -p{pwd} -r -aoa -o'{os.path.splitext(fn)[0]}'"
                    # print(cmd)
                    output = get_output(cmd)
                    ipwdtry += 1
                else:
                    need_new_pwd = True
                    break
            if need_new_pwd:
                while not "Everything is Ok" in ''.join(output):
                    pwd = input("\nEnter password: ")
                    cmd = f"7z x '{fn}' -p{pwd} -r -aoa -o'{os.path.splitext(fn)[0]}'"
                    print(cmd)
                    output = get_output(cmd)
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

    with open(passwordfile, 'w') as f:
        f.write(''.join(passwords))

    print('\n'.join(get_output("df -h `pwd`")))

    # print(f"{nExtracted} files extracted.")

    # print(get_output("cat passwords.txt"))


