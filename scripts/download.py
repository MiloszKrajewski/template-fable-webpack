import requests
import sys
import argparse
from shutil import copyfileobj
from urllib.parse import urlparse
from os.path import basename, isfile


def parse(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="source url")
    parser.add_argument("file", help="target file", nargs="?", default=None)
    parser.add_argument("--force", help="force download", action="store_true", default=False)
    return parser.parse_args(argv)
    
def main(args):
    url = args.url
    filename = args.file or basename(urlparse(url).path)

    if args.force or (not isfile(filename)):
        print("Downloading: {}".format(url))
        response = requests.get(url)
        print("Saving: {}".format(filename))
        with open(filename, 'wb') as target:
            target.write(response.content)
    else:
        print("Already exists: {}".format(filename))
    
if __name__=="__main__":
    sys.exit(main(parse(sys.argv[1:])))
