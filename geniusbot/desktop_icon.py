import winshell
from pathlib import Path
import os
import platform
import re
try:
    from geniusbot.version import __version__, __author__, __credits__
except Exception as e:
    from version import __version__, __author__, __credits__

# WINDOWS
# Define all the file paths needed for the shortcut
# Assumes default miniconda install
#desktop = Path(winshell.desktop())
desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
script_parent_dir = Path( __file__ ).parent.absolute().parent.absolute()
print(platform.python_version())
python_version = re.sub("\.", "", re.sub("\.[0-9][0-9]*$", "", platform.python_version()))
#miniconda_base = Path(winshell.folder('CSIDL_LOCAL_APPDATA')) / 'Continuum' / 'miniconda3'
base = Path(f"{Path(winshell.folder('CSIDL_LOCAL_APPDATA')).parent.absolute()}/Roaming/Python/Python{python_version}")
win32_cmd = str(Path(winshell.folder('CSIDL_SYSTEM')) / 'cmd.exe')
#icon = str(miniconda_base / "Menu" / "Iconleak-Atrous-Console.ico")
icon = str(script_parent_dir / "geniusbot" / "img" / "geniusbot.ico")

# This will point to My Documents/py_work. Adjust to your preferences
#my_working = str(Path(winshell.folder('CSIDL_PERSONAL')) / "py_work")
working_directory = str(Path(script_parent_dir))
link_filepath = str(desktop + "/Genius Bot.lnk")


# Build up all the arguments to cmd.exe
# Use /K so that the command prompt will stay open
# arg_str = "/K " + str(base / "Scripts" / "activate.bat") + " " + str(miniconda_base / "envs" / "work")
arg_str = "/K " + str("geniusbot")
print(f"Desktop: {desktop}\nBase: {base}\nScript Parent Directory: {script_parent_dir}\nwin32 Command: {win32_cmd}\nIcon: {icon}\nWorking Path: {working_directory}\nLink Path {link_filepath}\nArgs: {arg_str}")

# # Create the shortcut on the desktop
# with winshell.shortcut(link_filepath) as link:
#     link.path = win32_cmd
#     link.description = "Genius Bot"
#     link.arguments = arg_str
#     link.icon_location = (icon, 0)
#     link.working_directory = my_working

# Create the shortcut on the desktop
with winshell.shortcut(link_filepath) as link:
    link.path = win32_cmd
    link.description = "Genius Bot"
    link.arguments = arg_str
    link.icon_location = (icon, 0)
    link.working_directory = working_directory

# LINUX
with open(f"{desktop}/Genius Bot.desktop", "w") as desktop_icon:
    # Writing data to a file
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


