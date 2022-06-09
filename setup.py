#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
from geniusbot.version import __version__, __author__
from pathlib import Path
import re


readme = Path('README.md').read_text()
version = __version__
readme = re.sub(r"Version: [0-9]*\.[0-9]*\.[0-9][0-9]*", f"Version: {version}", readme)
print(f"README: {readme}")
with open("README.md", "w") as readme_file:
    readme_file.write(readme)
description = 'Synchronize your subtitle files by shifting the subtitle time (+/-)'

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
    packages=['geniusbot'],
    include_package_data=True,
    install_requires=['webarchiver', 'subshift', 'pandas', 'PyQt5', 'youtube-dl'],
    py_modules=['geniusbot'],
    package_data={'geniusbot': ['geniusbot']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: Public Domain',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={'console_scripts': ['geniusbot = geniusbot.geniusbot:main']},
)
