#!/bin/bash

# This script will install Python 3.X, 3.8, all required Python and Linux dependencies and Pycharm Community Editiion. 
# Update Packages
sudo yum -y update
# Install mlocate (Will be needed to locate pycharm.sh path
sudo yum -y install mlocate
sudo updatedb
# Install Python 3.X and 3.8
sudo yum install python3 -y
sudo yum install python38 -y
# Update PIP
sudo python3 -m pip install --upgrade pip
sudo python3.8 -m pip install --upgrade pip
# Install Python Depedencies
sudo yum install gcc python3-devel python38-devel openssl-devel tcl-thread xz-libs bzip2-devel libffi-devel python3-tkinter python38-tkinter -y 
# Install Python Packages
sudo python3 -m pip install autoconf setuptools wheel pytube3 regex requests tqdm selenium mutagen tkthread pillow twitter_scraper matplotlib numpy pandas scikit-learn scipy seaborn statsmodels more-itertools pyglet shapely piexif webdriver-manager pandas_profiling ipython-genutils traitlets jupyter-core pyrsistent jsonschema nbformat tornado pickleshare wcwidth prompt-toolkit parso jedi backcall pygments ipython pyzmq jupyter-client ipykernel Send2Trash prometheus-client pywinpty terminado testpath mistune packaging bleach entrypoints pandocfilters nbconvert notebook widgetsnbextension ipywidgets numba phik xlsxwriter paramiko cx_oracle pypyodbc sqlalchemy pyhive cx_freeze
sudo python3.8 -m pip install autoconf setuptools wheel pytube3 regex requests tqdm selenium mutagen tkthread pillow twitter_scraper matplotlib numpy pandas scikit-learn scipy seaborn statsmodels more-itertools pyglet shapely piexif webdriver-manager pandas_profiling ipython-genutils traitlets jupyter-core pyrsistent jsonschema nbformat tornado pickleshare wcwidth prompt-toolkit parso jedi backcall pygments ipython pyzmq jupyter-client ipykernel Send2Trash prometheus-client pywinpty terminado testpath mistune packaging bleach entrypoints pandocfilters nbconvert notebook widgetsnbextension ipywidgets numba phik xlsxwriter paramiko cx_oracle pypyodbc sqlalchemy pyhive cx_freeze
# Add EPEL repository
sudo yum install epel-release -y
# Install snapd package manager (Contains all depedencies packaged together)
sudo yum install snapd -y
# Systemmd unit that managed the main snap communication sockets needs to be enabled.
sudo systemctl enable --now snapd.socket
# Sleep for 5 seconds to allow for system link creation.
date +"%H:%M:%S"
sleep 5
date +"%H:%M:%S"
# To enable classic snap support, this creates a symbolic link between /var/lib/snapd/snap and /snap
sudo ln -s /var/lib/snapd/snap /snap
# Install PyCharm CE
sudo snap install pycharm-community --classic
# Locate PyCharm Installation Path 
sudo updatedb
pycharm_path=$(sudo locate pycharm.sh)
# Launch PyCharm as Root
echo $pycharm_path
