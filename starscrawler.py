#!/usr/bin/python3
from requests import get
from os import listdir, mkdir, path
from json import loads
from sys import argv
from argparse import *
from math import ceil
from colorama import Fore
from re import sub, IGNORECASE

class StarsCrawler:

    def __init__(self, args):
        self.user = args["u"]
        self.abso = path.dirname(path.realpath(__file__))
        self.path = self.abso + "/cache/" + self.user + "/"
        self.total = args["c"]
        self.count = (ceil(args["c"] / 100) if self.total is not None else 1) + 1
        self.logic = any if not args["and"] else all

        if args["flush"] or self.user not in listdir(self.abso + "/cache/"):
            if self.user not in listdir(self.abso + "/cache/"):
                mkdir(self.path)
            self.update_cache()

        self.search(args["keywords"])

    def update_cache(self):
        for i in range(1, self.count):
            stars = loads(get("https://api.github.com/users/{0}/starred?per_page=100&page={1}".format(self.user, i)).text)
            self.total = len(stars)
            print("found {} stars".format(self.total))
            x = 0
            for star in stars:
                url = "https://raw.githubusercontent.com/" + star["owner"]["login"] + "/" + star["name"] + "/master/README.md"
                readme = get(url)
                if readme.status_code == 200:
                    x += 1
                    out  = "[+] [{0}/{1}] Downloading => {2}".format(x, self.total, url)
                    print("\033[K", out, end="\r")
                    open(self.path + url.replace("/", "_"), "w").write(readme.text)


    def search(self, keywords):
        for star in listdir(self.path):
            if self.logic(word in open(self.path + star, "r").read().lower() for word in keywords):

                reg = r"https://raw\.githubusercontent\.com/([\-\w]+)/([\-\w]+)/master/README.md"
                print("==> " +sub(reg, r"https://github.com/" + Fore.BLUE + r"\1" + Fore.RESET +"/" + Fore.GREEN + r"\2" + Fore.RESET, star.replace("_", "/")))
                for line in open(self.path + star, "r"):
                    if any(word in line.lower() for word in keywords):
                        reg = r"("+"|".join(keywords) + ")"
                        print("    " + sub(reg, r"" + Fore.RED + r"\1" + Fore.RESET, line, flags=IGNORECASE)[:-1])
                print("")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-u', help="Username", required=True)
    parser.add_argument('-c', help="Your stars number", type=int)
    parser.add_argument('--flush', action="store_true", help="Refresh your stars")
    parser.add_argument('keywords', nargs="*")
    parser.add_argument('--and', help="must match all terms (default is or)", action="store_true")
    StarsCrawler(vars(parser.parse_args()))
