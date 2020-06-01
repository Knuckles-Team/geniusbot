Read me:

To run Cx_Freeze with TkThread. Make sure TkThread zip file is unziped in both the root Python>tcl folder AND Python>tcl>tcl8.6
SQLAlchemy must be copied and pasted from the origin every time.

Repository: https://github.com/Knucklessg1/genius-bot.git

Linux add thread tcl package: apt-get install tcl-thread

Add Chrome Extensions for Python Selenium:
https://stackoverflow.com/questions/34222412/load-chrome-extension-using-selenium
I did this with Python in case anyone was looking.

All you have to do is download the .crx file (I used https://chrome-extension-downloader.com/) and save it somewhere that Python can access it. In my example, I imported it to the same folder as my Python script, to load exampleOfExtensionDownloadedToFolder.crx.

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options 

options = webdriver.ChromeOptions()
options.add_extension('./exampleOfExtensionDownloadedToFolder.crx')
driver = webdriver.Chrome(chrome_options=options) 
driver.get('http://www.google.com')

Install Requirements:
Navigate to root folder and run: pip install -r requirements.txt

Run:
In PyCharm, or IDE of choice, run Smartbot.py to open the GUI.

To update pip:
pip install --upgrade pip

To update all python packages in venv:
../venv/Scripts/python.exe -m pip freeze | %{$_.split('==')[0]} | %{../venv/Scripts/python.exe -m pip install --upgrade $_}

To update all python packages:
pip freeze | %{$_.split('==')[0]} | %{pip install --upgrade $_}

To generate requirements file from venv:
../venv/Scripts/python.exe -m pip freeze > requirements.txt

To generate requirements file:
pip freeze > requirements.txt

To install requirements file into venv:
../venv/Scripts/python.exe -m pip install -r requirements.txt

To install requirements file:
pip install -r requirements.txt

IMPLEMENTING TKThread Library Requires This for CX_Freeze compilation.
To fix TkThread (Thread) not found issue. Copy Tkthread folder into 'venv>tcl>tcl8.6' as well as 'venv>tcl'

Install Microsoft Visual Studio C++ Distributable to install packages like PyHive!

IMPLEMENTED SQLAlchemy Library Requires manual copy from Python install directory. (Issue lies that SQLAlchemy always installs to Python install dir, instead of venv)

For Full Page Screenshots to Remove any Headers on Website that are fixed use this JQuery:
https://alisdair.mcdiarmid.org/kill-sticky-headers/

For Linux Selenium: Ensure Chromium is not snap version - https://askubuntu.com/questions/1075103/chromium-config-folder-is-missing-in-ubuntu-18-04
https://pypi.org/project/webdriver-manager/
