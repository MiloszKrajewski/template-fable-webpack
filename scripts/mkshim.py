import sys
import os
import argparse
import subprocess


def parse(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        help="source file (origin of the link, new file)")
    parser.add_argument(
        "target",
        help="target file (target of the link, existing file")
    parser.add_argument(
        "arguments", nargs="*", type=str,
        help="predefined arguments")
    return parser.parse_args(argv)


def decide_mode(target_file):
    _, ext = os.path.splitext(target_file)
    if ext == ".py":
        return "python"
    elif ext == ".pyw":
        return "pythonw"
    elif ext == ".js":
        return "node"
    else:
        return "call"


def main(args):
    current_folder = os.getcwd()
    source_file = os.path.join(current_folder, args.source)
    source_folder, _ = os.path.split(source_file)
    source_file = os.path.relpath(source_file, current_folder)
    target_file = os.path.join(current_folder, args.target)
    target_file = os.path.relpath(target_file, source_folder)
    mode = decide_mode(target_file)
    with open(source_file, "w") as target:
        arguments = ["%~dp0\\{}".format(target_file)]
        arguments.extend(args.arguments)
        arguments = subprocess.list2cmdline(arguments)
        arguments = "@{} {} %*".format(mode, arguments)
        target.write(arguments)
    return 0


if __name__ == "__main__":
    sys.exit(main(parse(sys.argv[1:])))
