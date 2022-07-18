#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
from geniusbot.version import __version__, __author__
from pathlib import Path
from glob import glob
import re
import os

readme = Path('README.md').read_text()
version = __version__
readme = re.sub(r"Version: [0-9]*\.[0-9]*\.[0-9][0-9]*", f"Version: {version}", readme)
print(f"README: {readme}")
with open("README.md", "w") as readme_file:
    readme_file.write(readme)
description = 'The Ever-learning and ever-improving tool!'

setup(
    name='geniusbot',
    version=f"{version}",
    description=description,
    long_description=f'{readme}',
    long_description_content_type='text/markdown',
    url='https://github.com/Knucklessg1/subsync',
    author=__author__,
    author_email='knucklessg1@gmail.com',
    license='Unlicense',
    packages=[
        'geniusbot',
    ],
    include_package_data=True,
    install_requires=[
        'webarchiver', 'subshift', 'pandas', 'PyQt5', 'youtube-dl', 'sqlalchemy', 'pytz', 'python-dateutil',
        'mathparse', 'pyyaml', 'winshell; platform_system == "Windows"', 'pypiwin32; platform_system == "Windows"',
        'torch', 'transformers', 'accelerate', 'media-downloader'
    ],
    py_modules=['geniusbot'],
    package_data={'geniusbot': ['geniusbot']},
    data_files=[
        ("geniusbot",  ["geniusbot/img/geniusbot.ico", "geniusbot/img/geniusbot.png"]),
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: Public Domain',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords=['genius', 'geniusbot', 'download', 'video', 'subtitle', 'website', 'screenshot'],
    entry_points={'console_scripts': ['geniusbot = geniusbot.geniusbot:main']},
)
