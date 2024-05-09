#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
from geniusbot.version import __version__, __author__
from pathlib import Path
import os
import re
from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements

readme = Path("README.md").read_text()
version = __version__
requirements = parse_requirements(
    os.path.join(os.path.dirname(__file__), "requirements.txt"), session=PipSession()
)
readme = re.sub(r"Version: [0-9]*\.[0-9]*\.[0-9]+", f"Version: {version}", readme)
with open("README.md", "w") as readme_file:
    readme_file.write(readme)
description = "The Ever-learning and ever-improving tool!"

setup(
    name="geniusbot",
    version=f"{version}",
    description=description,
    long_description=f"{readme}",
    long_description_content_type="text/markdown",
    url="https://github.com/Knuckles-Team/geniusbot",
    author=__author__,
    author_email="knucklessg1@gmail.com",
    license="MIT",
    packages=[
        "geniusbot",
        "geniusbot.qt",
        "geniusbot.plugins",
        "geniusbot.documentation",
    ],
    include_package_data=True,
    install_requires=[str(requirement.requirement) for requirement in requirements],
    extras_require={
        "media-manager": ["media-manager"],
        "media-downloader": ["media-downloader"],
        "webarchiver": ["webarchiver"],
        "subshift": ["subshift"],
        "report-manager": ["report-manager"],
        "rom-manager": ["rom-manager"],
        "repository-manager": ["repository-manager"],
        "audio-transcriber": ["audio-transcriber"],
        "all": [
            *sum(
                [
                    dependencies
                    for dependencies in [
                        ["media-manager"],
                        ["media-downloader"],
                        ["webarchiver"],
                        ["subshift"],
                        ["report-manager"],
                        ["rom-manager"],
                        ["repository-manager"],
                        ["audio-transcriber"],
                    ]
                ],
                [],
            )
        ],
    },
    py_modules=["geniusbot"],
    package_data={"geniusbot": ["geniusbot"]},
    data_files=[
        ("geniusbot", ["geniusbot/img/geniusbot.ico", "geniusbot/img/geniusbot.png"]),
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: Public Domain",
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=[
        "genius",
        "geniusbot",
        "download",
        "video",
        "subtitle",
        "website",
        "screenshot",
        "media",
        "manage",
        "chatbot",
        "report",
        "profiling",
        "merge",
    ],
    entry_points={"console_scripts": ["geniusbot = geniusbot.geniusbot:main"]},
)
