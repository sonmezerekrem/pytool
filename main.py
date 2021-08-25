import argparse
from src import passwordops
from src import fileops


parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("--password", help="Password operations")
parser.add_argument("--file", help="File operations")
parser.add_argument("--network", help="Network operations")

args = parser.parse_args()

if args.password and args.password == "create":
    passwordops.creator()
elif args.password and args.password == "read":
    passwordops.reader()
elif args.file and args.file == "info":
    fileops.information()
elif args.file and args.file == "size":
    fileops.size()
elif args.file and args.file == "rename":
    fileops.rename()
elif args.file and args.file == "compare":
    fileops.compare()
elif args.file and args.file == "backup":
    fileops.backup()
else:
    print("Pytool -> CLI tools for password, file and network management.")
