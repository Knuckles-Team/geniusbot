#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
from geniusbot.version import __version__, __author__
from pathlib import Path
from glob import glob
import re
import os
import sys
import platform
if sys.platform == 'win32':
    import winshell

readme = Path('README.md').read_text()
version = __version__
readme = re.sub(r"Version: [0-9]*\.[0-9]*\.[0-9][0-9]*", f"Version: {version}", readme)
print(f"README: {readme}")
with open("README.md", "w") as readme_file:
    readme_file.write(readme)
description = 'Synchronize your subtitle files by shifting the subtitle time (+/-)'


# Creates a Desktop shortcut to the installed software
def post_install():
    desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    script_parent_dir = Path( __file__ ).parent.absolute().parent.absolute()
    icon = str(script_parent_dir / "geniusbot" / "img" / "geniusbot.ico")
    working_directory = str(Path(script_parent_dir))
    if sys.platform == 'win32':
        python_version = re.sub("\.", "", re.sub("\.[0-9][0-9]*$", "", platform.python_version()))
        win32_cmd = str(Path(winshell.folder('CSIDL_SYSTEM')) / 'cmd.exe')
        link_filepath = str(desktop + "/Genius Bot.lnk")
        arg_str = "/K " + str("geniusbot")
        with winshell.shortcut(link_filepath) as link:
            link.path = win32_cmd
            link.description = "Genius Bot"
            link.arguments = arg_str
            link.icon_location = (icon, 0)
            link.working_directory = working_directory
    elif sys.platform == 'linux':
        with open(f"{desktop}/Genius Bot.desktop", "w") as desktop_icon:
            desktop_icon.write(
                f"[Desktop Entry]\n"
                f"Version={__version__}\n"
                f"Name=Genius Bot\n"
                f"Comment=Genius Bot\n"
                f"Exec=geniusbot\n"
                f"Icon={icon}\n"
                f"Path={working_directory}\n"
                f"Terminal=false\n"
                f"Type=Application\n"
                f"Categories=Utility;Application;\n"
            )

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
    install_requires=[
        'webarchiver', 'subshift', 'pandas', 'PyQt5', 'youtube-dl', 'sqlalchemy', 'pytz', 'python-dateutil',
        'mathparse', 'pyyaml', 'spacy', 'winshell', 'pypiwin32',
    ],
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

if sys.argv[1] == 'install':
    post_install()
