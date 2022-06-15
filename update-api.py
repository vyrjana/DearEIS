#!/usr/bin/env python3
from os import getcwd
from os.path import join
from typing import IO
from api_documenter import process  # github.com/vyrjana/python-api-documenter
import deareis
import deareis.plot.mpl


if __name__ == "__main__":
    output: str = process(
        title="DearEIS",
        modules_to_document=[
            deareis,
            deareis.plot.mpl,
        ],
        description=f"""
        """.strip(),
        minimal_classes=[],
        objects_to_ignore=[],
        latex_pagebreak=False,
    )
    fp: IO
    with open(join(getcwd(), "API-documentation.md"), "w") as fp:
        fp.write(output)
