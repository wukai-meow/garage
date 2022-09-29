#!/usr/bin/env python3
import os
import sys
import stat
import shutil
import signal
import urllib.request
import traceback
from subprocess import run
from glob import glob
from multiprocessing import Pool
from getopt import gnu_getopt as getopt

def move_autorename(src, dst):
    dst_dirname = os.path.dirname(dst)
    dst_basename = os.path.basename(dst)

    newdst = dst
    rename_num = 2
    while os.path.isfile(newdst) or os.path.isdir(newdst):
        newdst = dst_dirname + os.sep + dst_basename + '_' + str(rename_num)
        rename_num += 1
    shutil.move(src, newdst)


def get_output(cmd: str, raise_error=False) -> list:
    '''
    get output of a shell cmd. ignore error by default
    return: list of strings (one line per item, no \\n in the end)
    '''
    return str(run(cmd, shell=True, check=raise_error, capture_output=True).stdout, encoding='utf-8').split("\n")[:-1]

if __name__ == "__main__":
    my_dir = os.path.abspath(os.path.dirname(__file__))
    collect_dir = my_dir

    opts, args = getopt(sys.argv[1:], 'ud:', ['update', "dir="])
    for opt_name, opt_value in opts:
        if opt_name in ('-u', '--update'):
            get_output(
                f"wget https://raw.githubusercontent.com/wukai-meow/garage/main/collect.py -O {my_dir}{os.sep}collect.py")
            urllib.request.urlretrieve(
                "https://raw.githubusercontent.com/wukai-meow/garage/main/collect.py", my_dir+os.sep+"collect.py")
            os.chmod(my_dir+os.sep+"collect.py", 0o755)
            print("Upgraded.")
            sys.exit(0)
        if opt_name in ('-d', '--dir'):
            collect_dir = opt_value

    all_files = glob(collect_dir + '/**/*', recursive=True) # 包括目录名，难以清除
    
    for f_path in all_files:
        if os.path.isfile(f_path):
            move_autorename(f_path, collect_dir + os.sep + os.path.basename(f_path))
