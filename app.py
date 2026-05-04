#!/usr/bin/env python3

import requests
import os

NONPACKAGE_SIGNAL_FILELIST = ["cmd", "main.go"]

token = os.environ["GITHUB_TOKEN"]
headers = {"Authorization": f"Bearer {token}"}


def fetch_github_toplist():
    r = requests.get(
        "https://api.github.com/search/repositories?q=language:Go&sort=stars&order=desc&per_page=100",
        headers=headers,
    )
    r.raise_for_status()
    return r.json()


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
    for repo in fetch_github_toplist()["items"]:
        if check_package(repo["full_name"]):
            print(f"{i} - {repo['svn_url']} - {repo['stargazers_count']}")
            i = i + 1


if __name__ == "__main__":
    main()
