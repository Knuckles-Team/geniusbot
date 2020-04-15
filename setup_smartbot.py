import os.path

from cx_Freeze import setup, Executable

includefiles = ['img/', 'lib/', 'tcl86t.dll', 'tk86t.dll', 'README.txt', 'src/']
includes = ['tkinter', 'tkinter.ttk', 'selenium', 'schedule', 'sqlalchemy', 'multiprocessing', 'openpyxl', 'cryptography', 'time', 'argparse', 'pypyodbc', 'pathlib', 'PIL', 'json', 'testrail', 'timeit', 'datetime', 'pandas', 'numpy', 'requests', 'idna.idnadata', 'jira', 'cx_oracle', 'pyhive']
excludes = ['Tkinter']
packages = ['tkinter', 'selenium', 'openpyxl', 'schedule', 'multiprocessing', 'sqlalchemy', 'PIL', 'apscheduler', 'testrail', 'cryptography', 'json', 'pandas', 'numpy', 'testrail', 'requests', 'jira', 'appdirs', 'packaging', 'cx_oracle', 'pyhive'] #'pkg_resources._vendor']
build_exe_options = {'includes':includes, 'packages':packages, 'excludes':excludes, 'include_files':includefiles, 'build_exe': '..\\GeniusBot\\build\\GeniusBot'}
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')
setup(
    name = "GeniusBot",
    version = "1.00",
    description = "An Automation Tool Multiple Functionality at your fingertips",
    author = 'Audel Rouhi',
    author_email = 'Audel.Rouhi@.com',
    options = {'build_exe': build_exe_options},
    executables = [Executable("src/genius-bot.py", base = "Win32GUI")])#, icon="img/Smartbot.ico")])
