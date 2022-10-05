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


def get_output(cmd: str, raise_error=False) -> list:
    '''
    get output of a shell cmd. ignore error by default
    return: list of strings (one line per item, no \\n in the end)
    '''
    return str(run(cmd, shell=True, check=raise_error, capture_output=True).stdout, encoding='utf-8').split("\n")[:-1]


def update_toUnzipList(abandon_list=[]):
    '''返回相对路径'''
    compress_file_ext = ('7z', 'zip', 'rar', 'tar.gz', 'tar', 'tgz', '001', '002', '003', '004', '005', '006', '007', '008', '009',)
    fl = os.listdir()
    to_unzip = []
    for fn in fl:
        if not os.path.isdir(fn):
            if os.path.splitext(fn)[-1][1:] in compress_file_ext:
                if not os.path.isfile(fn+".aria2"):
                    to_unzip.append(fn)
    to_unzip = [x for x in to_unzip if x not in abandon_list]
    return to_unzip


def is_7z_exist():
    if not "Copyright" in "".join(get_output("7z --help")):
        return False
    else:
        return True


def move_if_in_sandboxie(zip_file_dir, to_unzip, moveto='F:\\Download\\'):
    if 'sandboxie' in zip_file_dir.lower() or 'defaultbox' in zip_file_dir.lower():
        for fn in to_unzip:
            move_autorename(fn, moveto + os.sep + fn)
        os.chdir(moveto)
        zip_file_dir = moveto
        to_unzip = update_toUnzipList()
    return zip_file_dir, to_unzip


def save_passwords(passwordfile: str, passwords: list):
    with open(passwordfile, 'w', encoding='utf-8') as f:
        f.write(''.join(passwords))


def is_size_zero(dir):
    size_MB = float(get_output("du '" + dir + "' -b --max-depth=0 | awk '{print $1}'")[0]) / 1024 / 1024
    if size_MB < 1:
        return True
    else:
        return False

def is_trash(fn):
    trash_kwds = ["萌次元", "喵子", "18moe", "请安装客户端"]
    isTrash = False
    for kwd in trash_kwds:
        if kwd in fn:
            isTrash = True
            break
    return isTrash


def get_root_dir_name(zip_file_dir, fn):
    found = False
    fnid = 1
    dirname = fn
    while not found:
        if fnid > 1000:
            raise IOError("找不到合适的文件夹id")
        fulldir = zip_file_dir+os.sep+dirname
        if (not os.path.isfile(fulldir)) and (not os.path.isdir(fulldir)):
            found = True
        else:
            fnid += 1
            dirname = fn + str(fnid)
    return dirname


def move_autorename(src, dst, collect=False):
    if collect == False:
        dst_dirname = os.path.dirname(dst)
        dst_basename = os.path.basename(dst)
        dstfn, dstext = os.path.splitext(dst_basename)

        newdst = dst
        rename_num = 2
        while os.path.isfile(newdst) or os.path.isdir(newdst):
            newdst = dst_dirname + os.sep + dstfn + '_' + str(rename_num) + dstext
            rename_num += 1
        shutil.move(src, newdst)
    elif collect == True:
        '''
        ./baidu/1.jpg
        ./google/1.jpg
        ->
        .baidu_1.jpg
        .google_1.jpg
        '''
        if not src.startswith("/"):
            src_relativepath = src
        else:
            src_relativepath = os.path.relpath(src, os.path.dirname(dst))
        shutil.move(src, os.path.dirname(dst)+'/'+src_relativepath.replace("/", "_"))


def remove_empty_folders(path_abs_or_rel):
    walk = list(os.walk(path_abs_or_rel))
    for path, _, _ in walk[::-1]:
        if len(os.listdir(path)) == 0:
            os.rmdir(path)


def is_all_remaining_skipped(skipped_list, to_unzip):
    # return set(skipped_list) == set(to_unzip)
    return all(item in skipped_list for item in to_unzip)


if __name__ == "__main__":
    my_dir = os.path.abspath(os.path.dirname(__file__))
    passwordfile = my_dir + os.sep + "passwords.txt"
    zip_file_dir = my_dir
    prefix7z = 'wsl ' if os.sep == '\\' else ""

    opts, args = getopt(sys.argv[1:], 'ud:', ['update', "dir="])
    for opt_name, opt_value in opts:
        if opt_name in ('-u', '--update'):
            print(get_output(
                f"wget https://raw.githubusercontent.com/wukai-meow/garage/main/auto7z.py -O {my_dir}{os.sep}auto7z.py"))
            urllib.request.urlretrieve(
                "https://raw.githubusercontent.com/wukai-meow/garage/main/auto7z.py", my_dir+os.sep+"auto7z.py")
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

    # 开始解压
    nExtracted = 0
    skipped_list = []
    abandon_list = []
    to_unzip = update_toUnzipList()
    zip_file_dir, to_unzip = move_if_in_sandboxie(zip_file_dir, to_unzip)
    total_nToUnzip = 0
    if not os.path.isdir("extracted"):
       os.mkdir("extracted")

    while len(to_unzip) != 0:
        total_nToUnzip += len(to_unzip)
        for fn in to_unzip:
            print(f"{nExtracted+len(skipped_list)+1}/{total_nToUnzip}\t{fn}")
            if not os.path.isfile(fn):
                print(f"{fn} was removed.")
                continue
            destdirname = get_root_dir_name(zip_file_dir, os.path.splitext(fn)[0])

            # # 多线程 # 发现有的文件夹没报错但解压完是空的，怀疑是因为有的被失败的覆盖了
            # def pool_exit(signum, frame):
            #     try:
            #         p.terminate()
            #     except:
            #         pass
            #     sys.exit(0)
            # signal.signal(signal.SIGTERM, pool_exit)
            # with Pool(processes=1) as p:
            #     poolres = []
            #     for ipwdtry, pwdp1 in enumerate(passwords):
            #         sys.stdout.write(
            #             f"\rTrying password {ipwdtry+1} / {len(passwords)}")
            #         sys.stdout.flush()
            #         pwd = pwdp1[:-1]
            #         cmd = f"cd {os.getcwd()}; {prefix7z} 7z x '{fn}' -p'{pwd}' -r -aoa -o'{destdirname}'"
            #         poolres.append(p.apply_async(get_output, args=(cmd,)))
            #     p.close()
            #     outputs = [''.join(r.get()) for r in poolres]
            #     p.join()

            # passwd_hit = '\\'
            # for iout, output in enumerate(outputs):
            #     if "Everything is Ok" in output:
            #         passwd_hit = passwords[iout]
            #         break
            # need_new_pwd = False if passwd_hit != '\\' else True

            # 单线程
            SKIP = False if not fn in skipped_list else True
            if not SKIP:
                # 正常解压，尝试所有密码
                need_new_pwd = True
                for ipwdtry, pwdp1 in enumerate(passwords):
                    sys.stdout.write(
                        f"\rTrying password {ipwdtry+1} / {len(passwords)}")
                    sys.stdout.flush()
                    pwd = pwdp1[:-1]
                    cmd = f"cd {os.getcwd()}; {prefix7z} 7z x '{fn}' -p'{pwd}' -r -aoa -o'{destdirname}'"
                    output = get_output(cmd)
                    if "Everything is Ok" in ''.join(output):
                        need_new_pwd = False
                        passwd_hit = pwd
                        break
                if need_new_pwd:
                    SKIP = True
                    skipped_list.append(fn)

            if is_all_remaining_skipped(skipped_list, to_unzip):
                # 如果只剩最后处理的，就逐一提示新密码
                try:
                    while not "Everything is Ok" in ''.join(output):
                        pwd = input("\nEnter password: ")
                        cmd = f"cd {os.getcwd()}; {prefix7z} 7z x '{fn}' -p'{pwd}' -r -aoa -o'{destdirname}'"
                        print(cmd)
                        output = get_output(cmd)
                        print("\n".join(output))
                    passwords.append(pwd + '\n')
                    save_passwords(passwordfile, passwords)
                    SKIP = False
                except KeyboardInterrupt:
                    # Ctrl+C的直接放弃解压
                    print(f"Abandon")
                    abandon_list.append(fn)
                    SKIP = True

            if not SKIP:
                # 解压是否成功，从文件大小再次确认
                if is_size_zero(destdirname):
                    print(f"Size of extracted {destdirname} is < 1 MB. Something wrong")
                    print(f"{passwd_hit=}")
                    SKIP = True
                    skipped_list.append(fn)

            if not SKIP:
                # 解压成功，清理文件
                try:
                    # 清理原压缩包
                    move_autorename(fn, "extracted" + os.sep + fn)
                    if fn.endswith(".001"):
                        num = 2
                        while True:
                            tryfile = fn.replace(".001", f'.00{num}')
                            if tryfile in to_unzip:
                                move_autorename(
                                    tryfile, "extracted" + os.sep + tryfile)
                                num += 1
                            else:
                                break
                    
                    # 清理解压后的文件
                    filelist = glob(destdirname+"/**", recursive=True)
                    for _f in filelist:
                        if is_trash(_f):
                            move_autorename(_f, "extracted" + os.sep + os.path.basename(_f))
                            print(_f, "moved to trash.")

                    filelist = glob(destdirname+"/**", recursive=True)
                    nfile = len(filelist)
                    if nfile <= 5:
                        for root_dir, cur_dir, files in os.walk(destdirname, topdown=False):
                            for _f in files:
                                move_autorename(root_dir + os.sep + _f,
                                                os.getcwd() + os.sep + _f, collect=True)
                        remove_empty_folders(destdirname)
                    else:
                        first_layer_ndirOrFiles = os.listdir(
                            destdirname)
                        if len(first_layer_ndirOrFiles) <= 2:
                            for ford in first_layer_ndirOrFiles:
                                move_autorename(os.path.splitext(fn)[0] + os.sep + ford, ford)
                            os.rmdir(root_dir)
                except Exception as e:
                    print("Exception during cleaning files:")
                    print(traceback.format_exc())
                finally:
                    nExtracted += 1
                    print("  Succeeded.")

        to_unzip = update_toUnzipList(abandon_list)

    if os.sep == '/':
        print('\n'.join(get_output("df -h `pwd`")))
    else:
        print('\n'.join(get_output(
            "Get-Volume -Driveletter " + zip_file_dir.split(":")[0])))

    print(f"{nExtracted} files extracted.")
    if len(abandon_list) != 0:
        print(f"{len(abandon_list)} files not extracted.")

    # print(get_output("cat passwords.txt"))
