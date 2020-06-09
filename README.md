# GeniusBot 
![Alt text](img/geniusbot-small.png?raw=true "GeniusBot") 

The Ever-learning and ever-improving tool!
- YouTube Archving
- Full Web Page Screenshots
- Report Merging
- Analytic Profiler

#### YouTube Archiving
![Alt text](screenshots/YouTubeArchive-small.png?raw=true "Report Merge")

#### WebPage Archiving
![Alt text](screenshots/WebArchive-small.png?raw=true "Report Merge")

#### Report Merging
![Alt text](screenshots/ReportMerge-small.png?raw=true "Report Merge")

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See Instructions for how to deploy the project on a live system.

## Repository
[genius-bot](https://github.com/Knucklessg1/genius-bot.git)

## Instructions to Run in PyCharm:
#### Pre-requisites:
```
1. PyCharm installed
2. Python 3.8 installed
3. pip install cx_freeze
4. (Optional) From root repository directory, run: pip install -r requirements.txt
```
#### Instructions:
```
1. In PyCharm, configure interpreter to use the virtual environment located in the repository (point it to the /venv/ folder)
2. In PyCharm, run GeniusBot.py to open the GUI.
```
## Instructions to Build Portable Version:
#### Pre-requisites:
```
1. pip install cx_freeze
2. (Optional) From root repository directory, run: pip install -r requirements.txt
```
#### Instructions:
```
1. To Compile install MSI file go to the build folder and open powershell in that directory.
2. Run the following command: ..\venv\Scripts\python .\setup.py build
or
2. (Only run this method if you've installed tcl-thread and requirements) Run the following command: python .\setup.py build
3. Another build folder will be generated with a GeniusBot.exe file inside. Open this file to run GeniusBot without installing
```
## Instructions to Compile Microsoft Installer File (MSI):
#### Pre-requisites:
```
1. pip install cx_freeze
2. (Optional) From root repository directory, run: pip install -r requirements.txt
```
#### Instructions:
```
1. To Compile install MSI file go to the build folder and open powershell in that directory.
2. Run the following command: ..\venv\Scripts\python .\setup.py bdist --format=msi
or
2. (Only run this method if you've installed tcl-thread and requirements) Run the following command: python .\setup.py bdist --format=msi
3. The setup.msi file will be generated in the dist folder located in the build folder.
```

## Bug Fixes and Issue Resolutions:
* To run Cx_Freeze with TkThread. Make sure TkThread zip file is unziped in both the root Python>tcl folder AND Python>tcl>tcl8.6
SQLAlchemy must be copied and pasted from the origin every time.

* Linux add thread tcl package: apt-get install tcl-thread or for Windows drag and drop tcl-thread packacge to tcl8.6 folder

* [Add Chrome Extensions for Python Selenium](https://stackoverflow.com/questions/34222412/load-chrome-extension-using-selenium)

* IMPLEMENTING TKThread Library Requires This for CX_Freeze compilation.
To fix TkThread (Thread) not found issue. Copy Tkthread folder into 'venv>tcl>tcl8.6' as well as 'venv>tcl'

* Install Microsoft Visual Studio C++ Distributable to install packages like PyHive!

* IMPLEMENTED SQLAlchemy Library Requires manual copy from Python install directory. (Issue lies that SQLAlchemy always installs to Python install dir, instead of venv)

* [For Full Page Screenshots to Remove any Headers on Website that are fixed use this JQuery](https://alisdair.mcdiarmid.org/kill-sticky-headers/)

* [For Linux Selenium: Ensure Chromium is not snap version](https://askubuntu.com/questions/1075103/chromium-config-folder-is-missing-in-ubuntu-18-04)

* [Web Driver Manager to Manage Selenium Drivers Automatically](https://pypi.org/project/webdriver-manager/)

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Built With

* Cx_Freeze
* Selenium
* Pandas
* Matplotlib
* PyTorch
* Chrome Web Driver
* FireFox Web Driver
* PyTube3
* Tkthread
* FFMPEG

## Versioning

Utilizing version_info.py to track version history.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
Please attribute any uses to this repository. Do not resale this application. Test
All credits to the FFMPEG team for the audio/video conversions
## Authors

* **Audel Rouhi** - *Sole Developer* - [knucklessg1](https://github.com/Knucklessg1)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## Acknowledgments

* tkthread - tclthread
* FFMPEG - All credits to the FFMPEG team for the audio/video conversions
## Pip Tips
#### To update pip:
```
pip install --upgrade pip
```
#### To update all python packages in venv:
```
../venv/Scripts/python.exe -m pip freeze | %{$_.split('==')[0]} | %{../venv/Scripts/python.exe -m pip install --upgrade $_}
```
#### To update all python packages:
```
pip freeze | %{$_.split('==')[0]} | %{pip install --upgrade $_}
```
#### To generate requirements file from venv:
```
../venv/Scripts/python.exe -m pip freeze > requirements.txt
```
#### To generate requirements file:
```
pip freeze > requirements.txt
```
#### To install requirements file into venv:
```
../venv/Scripts/python.exe -m pip install -r requirements.txt
```