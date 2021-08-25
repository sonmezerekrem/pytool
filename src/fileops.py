import filecmp
import os
import re
import shutil
import stat
from datetime import datetime

from tabulate import tabulate
from tqdm import tqdm


GB = 1073741824
MB = 1048576
KB = 1024


# https://stackoverflow.com/a/4368431
def size_calculation(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    # print("path: ",path)
    total_size = os.path.getsize(path)
    for item in os.listdir(path):
        #   print("filename: ",item)
        itempath = os.path.join(path, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += size_calculation(itempath)
    return total_size


def size_conversation(size):
    if size > GB:
        return "{:.2f}".format(size / GB) + " GB"
    elif size > MB:
        return "{:.2f}".format(size / MB) + " MB"
    elif size > KB:
        return "{:.2f}".format(size / KB) + " KB"
    else:
        return str(size) + " B"


def file_info(filepath):
    return {
        "Path": filepath,
        "Name": os.path.basename(filepath),
        "Extension": os.path.splitext(filepath)[1],
        "Size": size_conversation(os.path.getsize(filepath)),
        "Created": datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S'),
        "Edited": datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S'),
        "Permissions": stat.filemode(os.stat(filepath).st_mode)
    }


def directory_info(dirpath):
    return {
        "Path": dirpath,
        "Name": os.path.basename(dirpath),
        "Size": size_conversation(size_calculation(dirpath)),
        "Directories": len([name for name in os.listdir(dirpath) if os.path.isdir(os.path.join(dirpath, name))]),
        "Files": len([name for name in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, name))]),
        "Created": datetime.fromtimestamp(os.path.getctime(dirpath)).strftime('%Y-%m-%d %H:%M:%S'),
        "Edited": datetime.fromtimestamp(os.path.getmtime(dirpath)).strftime('%Y-%m-%d %H:%M:%S'),
    }


def information():
    inputpath = input("Path of directory or file: ")
    if os.path.isdir(inputpath):
        print("---DIRECTORY INFORMATION---")
        print(tabulate(directory_info(inputpath).items(), headers=["PROPERTY", "VALUE"]))
    elif os.path.isfile(inputpath):
        print("---FILE INFORMATION---")
        print(tabulate(file_info(inputpath).items(), headers=["PROPERTY", "VALUE"]))
    else:
        print("It is a special file (socket, FIFO, device file)")


def size():
    inputpath = input("Path of directory: ")
    if os.path.isdir(inputpath):
        print("---DIRECTORY SIZE INFORMATION---")
        sizes = {item: size_calculation(os.path.join(inputpath, item)) for item in os.listdir(inputpath)}
        max_items = sorted(sizes.items(), key=lambda item: item[1], reverse=True)[:8]
        max_items = [[item[0], size_conversation(item[1])] for item in max_items]
        print(tabulate(max_items, headers=["NAME", "SIZE"]))
    elif os.path.isfile(inputpath):
        print("---FILE SIZE INFORMATION---")
        print(tabulate(["Size", size_conversation(size_calculation(inputpath))], headers=["NAME", "SIZE"]))
    else:
        print("It is a special file (socket, FIFO, device file)")


def compare():
    inputpath1 = input("Path of first file: ")
    inputpath2 = input("Path of second file: ")

    if not (os.path.isfile(inputpath1) and os.path.isfile(inputpath2)):
        print("One of the paths is not a file!")
        return

    result = filecmp.cmp(inputpath1, inputpath2, shallow=True)

    if result:
        print("These files are same file")
    else:
        print("These files are not same")

    print("---DETAILS OF FIRST FILE---")
    print(tabulate(file_info(inputpath1).items(), headers=["PROPERTY", "VALUE"]))
    print("---DETAILS OF SECOND FILE---")
    print(tabulate(file_info(inputpath2).items(), headers=["PROPERTY", "VALUE"]))


def make_directory(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def check_existence(inputfile, destinationpath):
    files = os.listdir(destinationpath)
    for f in files:
        f = os.path.join(destinationpath, f)
        if filecmp.cmp(inputfile, f, shallow=True):
            return True
    return False


def save_backup_details(information, destination):
    filepath = os.path.join(destination, "pytoolbackuplog.txt")
    if os.path.isfile(filepath):
        with open(filepath, 'a') as f:
            for key, value in information.items():
                f.write('%s:%s\n' % (key, value))
            f.write("\n\n")
    else:
        with open(filepath, 'w') as f:
            for key, value in information.items():
                f.write('%s:%s\n' % (key, value))
            f.write("\n\n")


def copier(sourcepath, destinationpath, action, information):
    if os.path.isfile(sourcepath):
        make_directory(destinationpath)
        if check_existence(sourcepath, destinationpath):
            if action == 1:
                print(f"Skipping file to prevent overwritten: {sourcepath}")
                information["skipped"] += 1
            elif action == 2:
                name, extension = os.path.splitext(os.path.basename(sourcepath))
                shutil.copy2(sourcepath, os.path.join(destinationpath, f"{name}_copy{extension}"))
                information["renamed"] += 1
                pass
            else:
                print(f"File is overwritten: {sourcepath}")
                shutil.copy2(sourcepath, destinationpath)
                information["overwritten"] += 1
        else:
            shutil.copy2(sourcepath, destinationpath)
            information["copied"] += 1
    elif os.path.isdir(sourcepath):
        sourcefiles = os.listdir(sourcepath)
        for item in sourcefiles:
            itempath = os.path.join(sourcepath, item)
            if os.path.isfile(itempath):
                copier(itempath, destinationpath, action, information)
            elif os.path.isdir(itempath):
                make_directory(destinationpath)
                copier(itempath, os.path.join(destinationpath, item), action, information)


def backup():
    sourcepath = input("Path of the source directory: ")
    destinationpath = input("Path of the destination directory: ")
    action = int(input("Action for duplicate files (1) for skip, (2) for rename, (3) for overwritten: "))

    if not (os.path.isdir(sourcepath) and os.path.isdir(destinationpath)):
        print("One of the paths is not a directory!")
        return

    if action != 1 and action != 2 and action != 3:
        action = 2

    if re.search(".*20[0-9][0-9]-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])", os.path.basename(destinationpath)):
        newdestination = destinationpath[:-10] + datetime.now().strftime('%Y-%m-%d')
    else:
        newdestination = destinationpath + datetime.now().strftime('%Y-%m-%d')
    os.rename(destinationpath, newdestination)
    destinationpath = newdestination

    information = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "copied": 0,
        "skipped": 0,
        "overwritten": 0,
        "renamed": 0,
        "source": sourcepath,
        "destination": destinationpath,
    }

    sourcefiles = os.listdir(sourcepath)
    for item in tqdm(sourcefiles, desc="COPYING FILES: "):
        itempath = os.path.join(sourcepath, item)
        if os.path.isfile(itempath):
            copier(itempath, destinationpath, action, information)
        elif os.path.isdir(itempath):
            copier(itempath, os.path.join(destinationpath, item), action, information)

    save_backup_details(information, destinationpath)


def rename():
    inputdir = input("Path of the directory: ")
    prefix = input("Prefix for new names: ")

    if os.path.isdir(inputdir):
        filelist = os.listdir(inputdir)
        i = 1
        for f in tqdm(filelist, desc="RENAMING FILES:   "):
            filepath = os.path.join(inputdir, f)
            if os.path.isfile(filepath):
                _, extension = os.path.splitext(filepath)
                newname = os.path.join(inputdir, f"{prefix}_{i}{extension}")
                os.rename(filepath, newname)
                i += 1
    print(f"Renamed all files in {inputdir}")

