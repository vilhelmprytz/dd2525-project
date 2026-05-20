#!/usr/bin/env python3

__author__ = "Vilhelm Prytz & Filip Dimitrijevic"

FILENAME = "curated_toplist_repositories.txt"
DOCKER_IMAGENAME = "dd2525-project-capslock"
RESULT_DIR = "results"
NUM_VERSIONS = 5

import os
import re
import pathlib
import requests
import docker
from tqdm import tqdm

token = os.environ["GITHUB_TOKEN"]
headers = {"Authorization": f"Bearer {token}"}


def read_repolist(filename: str):
    f = open(filename, "r")
    raw = f.read()
    f.close()

    res = []
    for l in raw.split("\n"):
        if l:
            res.append(l)
    return res


def get_tags(clone_url: str, n: int = NUM_VERSIONS) -> list[str]:
    repo_path = clone_url.split("https://github.com/")[1].split(".git")[0]
    url = f"https://api.github.com/repos/{repo_path}/tags"
    tags = []
    page = 1
    while True:
        resp = requests.get(
            url, headers=headers, params={"per_page": 100, "page": page}
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        tags.extend(t["name"] for t in batch)
        page += 1

    semver = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
    parsed = []
    for t in tags:
        m = semver.match(t)
        if m:
            parsed.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), t))

    # pick highest patch per (major, minor), then take last n minors
    by_minor = {}
    for major, minor, patch, name in parsed:
        key = (major, minor)
        if key not in by_minor or patch > by_minor[key][0]:
            by_minor[key] = (patch, name)

    selected = sorted(by_minor.items())[-n:]
    return [name for _, (_, name) in selected]


def build_docker_image(client: docker.DockerClient):
    image, _ = client.images.build(path=".", tag=DOCKER_IMAGENAME, rm=True)
    return image


def run_capslock(
    client: docker.DockerClient,
    docker_image: docker.models.images.Image,
    clone_url: str,
    out_dir: str,
    tag: str,
):
    repo_name = (
        clone_url.split("https://github.com/")[1].split(".git")[0].replace("/", "_")
    )
    repo_out = pathlib.Path(f"{out_dir}/{repo_name}")
    repo_out.mkdir(parents=True, exist_ok=True)
    (repo_out / f"{tag}.json").touch()

    cmd = (
        f"git clone --depth 1 --branch {tag} {clone_url} /src && "
        f"cd /src && "
        f"go mod download && "
        f"capslock -output=json -packages ./... > /results/{tag}.json"
    )

    container = client.containers.run(
        docker_image,
        command=["/bin/sh", "-c", cmd],
        volumes={str(repo_out.resolve()): {"bind": "/results", "mode": "rw"}},
        detach=True,
    )
    result = container.wait()
    if result["StatusCode"] != 0:
        logs = container.logs().decode("utf-8")
        (repo_out / f"{tag}.error.log").write_text(
            f"repo: {clone_url}\ntag: {tag}\nexitcode: {result['StatusCode']}\n\n{logs}"
        )
        print(f"ERROR: {clone_url}@{tag} exited with code {result['StatusCode']}")
    container.remove()


def main():
    repolist = read_repolist(FILENAME)
    print(f"Using {FILENAME} with top {len(repolist)} repositories")

    print(f"Building Docker image {DOCKER_IMAGENAME}")
    client = docker.from_env()
    image = build_docker_image(client)

    print(f"Running capslock on all repositories")
    for repo in tqdm(repolist):
        tags = get_tags(repo)
        if not tags:
            print(f"WARNING: no semver tags found for {repo}, skipping")
            continue
        for tag in tags:
            run_capslock(client, image, repo, RESULT_DIR, tag=tag)


if __name__ == "__main__":
    main()
