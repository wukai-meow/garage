#!/usr/bin/env python3
import os
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


if not os.path.isfile("passwords.txt"):
    with open("passwords.txt", 'w') as f:
        f.write("\n")

# print(get_output("cat passwords.txt"))
with open("passwords.txt", 'r') as f:
    passwords = f.readlines()

if not os.path.isdir("extracted"):
    os.mkdir("extracted")

nExtracted = 0
to_unzip = update_toUnzipList()
while len(to_unzip) != 0:
    for fn in to_unzip:
        nsavedpwd = len(passwords)
        need_new_pwd = False
        ipwdtry = 0
        output = ''
        while not "Everything is Ok" in ''.join(output):
            if ipwdtry < nsavedpwd:
                pwd = passwords[ipwdtry][:-1]
                cmd = f"7z x '{fn}' -p{pwd} -r -aoa -o'{os.path.splitext(fn)[0]}'"
                print(cmd)
                output = get_output(cmd)
                ipwdtry += 1
            else:
                need_new_pwd = True
                break
        if need_new_pwd:
            while not "Everything is Ok" in ''.join(output):
                pwd = input("Enter password: ")
                cmd = f"7z x '{fn}' -p{pwd} -r -aoa -o'{os.path.splitext(fn)[0]}'"
                print(cmd)
                output = get_output(cmd)
            passwords.append(pwd + '\n')
        os.rename(fn, "extracted/"+fn)

        if len(os.listdir(os.path.splitext(fn)[0])) < 10:
            get_output(f"mv '{os.path.splitext(fn)[0]}'/* ./ && trash '{os.path.splitext(fn)[0]}'")
        nExtracted += 1

    to_unzip = update_toUnzipList()

with open("passwords.txt", 'w') as f:
    f.write(''.join(passwords))

print(f"{nExtracted} files extracted.")

# print(get_output("cat passwords.txt"))


