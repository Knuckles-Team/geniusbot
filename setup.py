import os
import sys

from cx_Freeze import setup, Executable
#https://stackoverflow.com/questions/35533803/keyerror-tcl-library-when-i-use-cx-freeze
#https://gist.github.com/nicoddemus/ca0acd93a20acbc42d1d

company_name = 'WebArchive'
product_name = 'GeniusBot'
python_install_dir = os.path.dirname(os.path.dirname(os.__file__))
parent_dir = str(os.pardir) + "/"
build_dir = str(parent_dir) + "/build/"
src_dir = str(parent_dir) + "/src/"
img_dir = str(parent_dir) + "/img/"
lib_dir = str(parent_dir) + "/lib/"
logs_dir = str(parent_dir) + "/logs/"
fonts_dir = str(parent_dir) + "/fonts/"

base = None
if sys.platform == "win32":
    base = "Win32GUI"

os.environ['TCL_LIBRARY'] = os.path.join(python_install_dir, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(python_install_dir, 'tcl', 'tk8.6')
includefiles = ['src/', 'lib/', 'img/', 'logs/', 'fonts/', 'README.txt', os.path.join(python_install_dir, 'DLLs', 'tk86t.dll'),
            os.path.join(python_install_dir, 'DLLs', 'tcl86t.dll')]#'tcl86t.dll', 'tk86t.dll']
includes = ['os','sys','ctypes', 'Screenshot', 'pywb', 'joblib', 'pyglet', 'pytube', 'urllib', 're', 'platform', 'tqdm', 'tkinter', 'mutagen', 'requests', 'subprocess', 'threading', 'tkthread', 'tkinter.ttk', 'selenium', 'PIL', 'numpy', 'pandas', 'time']
packages = ['os','sys','ctypes', 'Screenshot', 'pywb', 'joblib', 'pyglet', 'pytube', 'urllib', 're', 'platform', 'tqdm', 'tkinter', 'mutagen', 'requests', 'subprocess', 'threading', 'tkthread', 'tkinter.ttk', 'selenium', 'PIL', 'numpy', 'pandas', 'time']
excludes = ['PyQt4', 'PyQt5', 'Tkinter', 'sqlalchemy', 'cryptography',  'pypyodbc', 'json', 'appdirs', 'packaging', 'cx_oracle', 'pyhive', 'spaCy']
build_exe_options = {
    'packages': packages,
    'includes': includes,
    'include_files': includefiles,
    'include_msvcr': True,
    'add_to_path': True,
    # Sometimes a little fine-tuning is needed
    # exclude all backends except wx
    'excludes': excludes
	#'build_exe': '..\\GeniusBot\\build\\GeniusBot'
}

bdist_msi_options = {
    'upgrade_code': '{66620F3A-DC3A-11E2-B341-002219E9B01E}',
    'add_to_path': False,
    'initial_target_dir': r'[ProgramFilesFolder]\%s\%s' % (company_name, product_name),
    # 'includes': ['atexit', 'PySide.QtNetwork'], # <-- this causes error
}

setup(
    name = "GeniusBot - Web Archive",
    author = 'Knux',
    version = "1.0",
    description = "A tool to archive the internet",
    options = {'build_exe': build_exe_options,
               'bdist_msi': bdist_msi_options},
    executables = [Executable(script='src/genius-bot.py', base=base, targetName='GeniusBot.exe')]
)
