from os import (
    makedirs,
    remove,
    walk,
)
from os.path import (
    basename,
    exists,
    isdir,
    join,
    splitext,
)
from shutil import (
    copy,
    copytree,
    rmtree,
)
from typing import List


def copy_html(src: str, dst: str):
    if exists(dst):
        rmtree(dst)
    files: List[str] = []
    for _, _, files in walk(src):
        break
    assert len(files) > 0
    files = [
        _
        for _ in files
        if not _.startswith(".")
        and splitext(_)[1]
        in (
            ".html",
            ".js",
            ".py",
            ".png",
            ".pdf",
        )
    ]
    dirs: List[str] = ["_images", "_static"]
    if not isdir(dst):
        makedirs(dst)
    name: str
    for name in files:
        copy(join(src, name), join(dst, name))
    for name in dirs:
        copytree(join(src, name), join(dst, name))


def copy_pdf(src: str, dst: str, version_path: str):
    version: str = ""
    with open(version_path, "r") as fp:
        version = fp.read().strip().replace(".", "-")
    assert version != ""
    name: str
    ext: str
    name, ext = splitext(basename(src))
    dst = join(dst, f"{name} - {version}{ext}")
    if exists(dst):
        remove(dst)
    copy(src, dst)


if __name__ == "__main__":
    copy_html(
        src="./docs/build/html",
        dst="./dist/html",
    )
    copy_pdf(
        src="./docs/build/latex/latex/deareis.pdf",
        dst="./dist",
        version_path="./version.txt",
    )
