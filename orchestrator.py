#!/usr/bin/env python3

__author__ = "Vilhelm Prytz & Filip Dimitrijevic"

FILENAME = "curated_toplist_repositories.txt"
DOCKER_IMAGENAME = "dd2525-project-capslock"
RESULT_DIR = "results"

import pathlib
import docker
from tqdm import tqdm


def read_repolist(filename: str):
    f = open(filename, "r")
    raw = f.read()
    f.close()

    res = []
    for l in raw.split("\n"):
        if l:
            res.append(l)
    return res


def build_docker_image(client: docker.DockerClient):
    image, _ = client.images.build(path=".", tag=DOCKER_IMAGENAME, rm=True)
    return image


def run_capslock(
    client: docker.DockerClient,
    docker_image: docker.models.images.Image,
    clone_url: str,
    out_dir: str,
    tag: str = "latest",
):
    repo_name = (
        clone_url.split("https://github.com/")[1].split(".git")[0].replace("/", "_")
    )
    repo_out = pathlib.Path(f"{out_dir}/{repo_name}")
    repo_out.mkdir(parents=True, exist_ok=True)

    cmd = (
        f"git clone --depth 1 {clone_url} /src && "
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
        run_capslock(client, image, repo, RESULT_DIR)


if __name__ == "__main__":
    main()
