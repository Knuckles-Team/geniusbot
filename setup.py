#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
from geniusbot.version import __version__, __author__
from pathlib import Path
import re

readme = Path('README.md').read_text()
version = __version__
readme = re.sub(r"Version: [0-9]*\.[0-9]*\.[0-9]+", f"Version: {version}", readme)
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
    url='https://github.com/Knuckles-Team/geniusbot',
    author=__author__,
    author_email='knucklessg1@gmail.com',
    license='Unlicensed',
    packages=[
        'geniusbot',
    ],
    include_package_data=True,
    install_requires=[
        'PyQt5>=5.15.7', 'winshell>=0.6; platform_system == "Windows"', 'pypiwin32; platform_system == "Windows"',
        'torch>=1.13.1', 'transformers>=4.25.1', 'accelerate>=0.15.0', "tabulate>=0.9.0", "psutil>=5.9.4",
        'media-downloader>=0.1.1', 'webarchiver>=0.4.0', 'subshift>=0.6.0', 'genius-chatbot>=0.2.0',
        'media-manager>=0.1.1', 'report-manager>=0.6.0', 'repository-manager>=0.2.1', 'systems-manager>=0.2.0',
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
