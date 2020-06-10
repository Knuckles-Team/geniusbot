#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
# import matplotlib
# from mpl_toolkits import axes_grid, axes_grid1


from pathlib import Path
from cx_Freeze import setup, Executable

# https://stackoverflow.com/questions/35533803/keyerror-tcl-library-when-i-use-cx-freeze
# https://gist.github.com/nicoddemus/ca0acd93a20acbc42d1d

parent_dir = Path(__file__).resolve().parents[1]
python_install_dir = os.path.dirname(os.path.dirname(os.__file__))
# parent_dir = str(os.getos.pardir) + "/"
build_dir = str(parent_dir) + "/build/"
src_dir = str(parent_dir) + "/src/"
img_dir = str(parent_dir) + "/img/"
lib_dir = str(parent_dir) + "/lib/"
logs_dir = str(parent_dir) + "/logs/"
fonts_dir = str(parent_dir) + "/fonts/"
# Don't append parent_dir, it will contain build folder and recursively scan itself.
# sys.path.append(parent_dir)
sys.path.append(src_dir)

from version_info import geniusbot_version

company_name = 'WebArchive'
product_name = 'GeniusBot'
version = f'{geniusbot_version}'

base = None
if sys.platform == "win32":
    base = "Win32GUI"

os.environ['TCL_LIBRARY'] = os.path.join(python_install_dir, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(python_install_dir, 'tcl', 'tk8.6')
include_files = [src_dir, lib_dir, img_dir, logs_dir, fonts_dir,
                 str(os.path.join(python_install_dir, 'DLLs', 'tk86t.dll')),
                 str(os.path.join(python_install_dir, 'DLLs', 'tcl86t.dll'))]

includes = ['os', 'sys', 'ctypes', 'pathlib', 'logging', 'urllib.request', 'json', 'joblib', 'pyglet', 'pytube',
            'urllib', 're', 'platform', 'tqdm', 'tkinter', 'mutagen', 'requests', 'subprocess', 'threading', 'tkthread',
            'tkinter.ttk', 'selenium', 'PIL', 'numpy', 'pandas', 'time', 'piexif', 'webdriver_manager', 'appdirs',
            'pandas_profiling', 'sklearn', 'scipy', 'seaborn', 'math', 'xlsxwriter', 'multiprocessing',
            'astropy.constants.codata2018', 'astropy.constants.iau2015', 'matplotlib', 'matplotlib.pyplot',
            'pkg_resources']

packages = includes

excludes = ['PyQt4', 'PyQt5', 'Tkinter', 'sqlalchemy', 'cryptography', 'pypyodbc', 'packaging', 'cx_oracle',
            'pyhive', 'spaCy', 'scipy.spatial.cKDTree']
build_exe_options = {
    'packages': packages,
    'includes': includes,
    'include_files': include_files,
    'include_msvcr': True,
    'add_to_path': True,
    # 'build_exe': 'GeniusBot',
    # Sometimes a little fine-tuning is needed
    # exclude all backends except wx
    'excludes': excludes
}

# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
# https://stackoverflow.com/questions/15734703/use-cx-freeze-to-create-an-msi-that-adds-a-shortcut-to-the-desktop
# https://stackoverflow.com/questions/51560822/python-cx-freeze-shortcut-icon
shortcut_table = [
    ("DesktopShortcut",  # Shortcut
     "DesktopFolder",  # Directory_
     "GeniusBot",  # Name
     "TARGETDIR",  # Component_
     "[TARGETDIR]GeniusBot.exe",  # Target
     None,  # Arguments
     "None",  # Description
     None,  # Hotkey
     "",  # Icon
     0,  # IconIndex
     None,  # ShowCmd
     'TARGETDIR'  # WkDir
     )
]

msi_data = {"Shortcut": shortcut_table}

bdist_msi_options = {
    'data': msi_data,
    'upgrade_code': '{66620F3A-DC3A-11E2-B341-002219E9B01E}',
    'add_to_path': False,
    'initial_target_dir': r'[ProgramFilesFolder]\%s\%s' % (company_name, product_name),
}

setup(
    name="GeniusBot",
    author='MajesticMajesty',
    version=version,
    description="Multi-Functional Bot",
    options={'build_exe': build_exe_options,
             'bdist_msi': bdist_msi_options},
    executables=[Executable(script=f'{src_dir}genius-bot.py', base=base, targetName='GeniusBot.exe',
                            icon=f'{img_dir}geniusbot.ico')]
)
