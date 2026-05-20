#!/usr/bin/env python3

import requests
import os
import math

NONPACKAGE_SIGNAL_FILELIST = ["cmd", "main.go"]
FILENAME = "toplist_repositories.txt"

token = os.environ["GITHUB_TOKEN"]
headers = {"Authorization": f"Bearer {token}"}


def fetch_github_toplist(n: int = 500):
    pages = math.ceil(n / 100)
    res = []
    for i in range(1, pages + 1):
        r = requests.get(
            f"https://api.github.com/search/repositories?q=language:Go&sort=stars&order=desc&per_page=100&page={i}",
            headers=headers,
        )
        r.raise_for_status()
        res.extend(r.json()["items"])
    return res


def check_package(full_name: str):
    r = requests.get(
        f"https://api.github.com/repos/{full_name}/contents/", headers=headers
    )
    r.raise_for_status()
    for f in NONPACKAGE_SIGNAL_FILELIST:
        if any(d["path"] == f for d in r.json()):
            return False
    return True


def main():
    i = 1
    repos = []
    for repo in fetch_github_toplist():
        if check_package(repo["full_name"]):
            print(f"{i} - {repo['clone_url']} - {repo['stargazers_count']}")
            i = i + 1
            repos.append(repo["clone_url"])

    f = open(FILENAME, "w")
    for repo in repos:
        f.write(repo + "\n")
    f.close()
    print(f"Wrote top repositories to {FILENAME}")


if __name__ == "__main__":
    main()
