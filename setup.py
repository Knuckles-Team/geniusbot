#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
from geniusbot.version import __version__, __author__
from pathlib import Path
from glob import glob
import re
import os
import sys

if sys.platform == 'win32':
    dependencies = [
        'webarchiver', 'subshift', 'pandas', 'PyQt5', 'youtube-dl', 'sqlalchemy', 'pytz', 'python-dateutil',
        'mathparse', 'pyyaml', 'spacy', 'winshell', 'pypiwin32',
    ]
else:
    dependencies = [
        'webarchiver', 'subshift', 'pandas', 'PyQt5', 'youtube-dl', 'sqlalchemy', 'pytz', 'python-dateutil',
        'mathparse', 'pyyaml', 'spacy',
    ]

readme = Path('README.md').read_text()
version = __version__
readme = re.sub(r"Version: [0-9]*\.[0-9]*\.[0-9][0-9]*", f"Version: {version}", readme)
print(f"README: {readme}")
with open("README.md", "w") as readme_file:
    readme_file.write(readme)
description = 'The Ever-learning and ever-improving tool!'

root = 'en_core_web_sm'
en_core_web_sm_list = []
for path, subdirs, files in os.walk(root):
    for name in files:
        en_core_web_sm_list.append(str(os.path.join(path, name)))
        print("FILE: ", os.path.join(path, name))

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
        'chatterbot',
        'chatterbot.storage',
        'chatterbot.logic',
        'chatterbot.ext',
        'chatterbot.ext.sqlalchemy_app',
        'chatterbot_corpus',
        'en_core_web_sm'
    ],
    include_package_data=True,
    install_requires=dependencies,
    py_modules=['geniusbot'],
    package_data={'geniusbot': ['geniusbot']},
    data_files=[
        ("geniusbot",  ["geniusbot/img/geniusbot.ico", "geniusbot/img/geniusbot.png"]),
        ('chatterbot_corpus', glob('chatterbot_corpus/data/*/*.yml', recursive=True)),
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: Public Domain',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords=['genius', 'geniusbot', 'download', 'video', 'subtitle', 'website', 'screenshot'],
    entry_points={'console_scripts': ['geniusbot = geniusbot.geniusbot:main']},
)
