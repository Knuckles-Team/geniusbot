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
    url='https://github.com/Knucklessg1/genius-bot',
    author=__author__,
    author_email='knucklessg1@gmail.com',
    license='Unlicense',
    packages=[
        'geniusbot',
    ],
    include_package_data=True,
    install_requires=[
        'webarchiver', 'subshift', 'PyQt5', 'winshell; platform_system == "Windows"',
        'pypiwin32; platform_system == "Windows"', 'torch', 'transformers', 'accelerate', 'media-downloader>=0.0.2',
        'media-manager>=0.0.5', 'report-manager>=0.0.1',
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
        'Programming Language :: Python :: 3.11',
    ],
    keywords=['genius', 'geniusbot', 'download', 'video', 'subtitle', 'website', 'screenshot', 'media', 'manage',
              'chatbot', 'report', 'profiling', 'merge'],
    entry_points={'console_scripts': ['geniusbot = geniusbot.geniusbot:main']},
)
