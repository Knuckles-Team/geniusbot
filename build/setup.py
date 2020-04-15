import os
import sys

from cx_Freeze import setup, Executable

python_install_dir = os.path.dirname(os.path.dirname(os.__file__))
parent_dir = str(os.pardir) + "/"
build_dir = str(parent_dir) + "/build/"
src_dir = str(parent_dir) + "/src/"
img_dir = str(parent_dir) + "/img/"
lib_dir = str(parent_dir) + "/lib/"

base = None
if sys.platform == "win32":
    base = "Win32GUI"

os.environ['TCL_LIBRARY'] = os.path.join(python_install_dir, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(python_install_dir, 'tcl', 'tk8.6')
includefiles = [f'{src_dir}youtube_download.py', f'{src_dir}webpage_archive.py', src_dir, lib_dir, img_dir, f'{parent_dir}README.txt', src_dir, f'{parent_dir}tcl86t.dll', f'{parent_dir}tk86t.dll'] #f'{parent_dir}tcl86t.dll', f'{parent_dir}tk86t.dll'
packages = ['os','sys','ctypes', 're', 'time', 'joblib', 'pytube', 'urllib', 're', 'platform', 'tqdm', 'tkinter', 'mutagen', 'requests', 'subprocess', 'threading', 'tkthread', 'tkinter.ttk', 'selenium', 'sqlalchemy', 'multiprocessing', 'PIL', 'cryptography', 'time', 'json', 'pandas', 'numpy', 'requests', 'appdirs', 'packaging', 'cx_oracle', 'pyhive']
includes = ['os','sys','ctypes', 're', 'time', 'joblib', 'pytube', 'urllib', 're', 'platform', 'tqdm', 'tkinter', 'mutagen', 'requests', 'subprocess', 'threading', 'tkthread', 'tkinter.ttk', 'selenium', 'sqlalchemy', 'multiprocessing', 'PIL', 'cryptography', 'time', 'json', 'pandas', 'numpy', 'requests', 'appdirs', 'packaging', 'cx_oracle', 'pyhive']
excludes = ['PyQt4', 'PyQt5', 'Tkinter']
build_exe_options = {
    'packages': packages,
    'includes': includes,
    'include_files': includefiles,
    'include_msvcr': True,
    # Sometimes a little fine-tuning is needed
    # exclude all backends except wx
    'excludes': excludes,
	'build_exe': '..\\build\\GeniusBot'
}

setup(
    name = "GeniusBot - Web Archive",
    author = 'Knux',
    version = "1.0",
    description = "A tool to archive the internet",
    options = {'build_exe': build_exe_options},
    executables = [Executable(script=f'{src_dir}genius-bot.py', base=base, targetName=f"GeniusBot.exe")]
)
