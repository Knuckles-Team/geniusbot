# GeniusBot 
*Version: 2.0.0*
![Alt text](geniusbot/img/geniusbot-small.png?raw=true "GeniusBot") 

The Ever-learning and ever-improving tool!
- YouTube Archiving
- Web Page Archiving
- Report Merging
- Analytic Profiler
- Twitter Archiving

Features Coming Soon
- Video/Audio Converter
- Chat Rooms

[Download GeniusBot Installer for Windows](https://github.com/Knucklessg1/genius-bot/releases/download/v1.8.2/GeniusBot-1.8.2-amd64.msi)

#### Video Download
Download any YouTube video(s) as MP3 or Webm/MP4 in a few different qualities. 
![YouTube Archive Image](screenshots/YouTubeArchive-small.png?raw=true "YouTube Archive")

Examples for how to find user & channel.
![User Entry Image](screenshots/user.PNG?raw=true "User Entry")
![Channel Entry Image](screenshots/channel.PNG?raw=true "Channel Entry")

Open File allows you to browse for a text file that has a list of YouTube links.
Examples contents:
```
https://www.youtube.com/watch?v=75-siCngYCc
https://www.youtube.com/watch?v=7RSpZkIjK4w
https://www.youtube.com/watch?v=7qRSAUb96wg
```
#### Website Archiving
Archive any website by taking screenshots of any website entered.

Choose from a variety of options like file type, quality, and image size.

More to come...

![Web Archive Image](screenshots/WebArchive-small.png?raw=true "Web Archive")

#### Report Merging
Take two CSV/Excel files and join them on whatever columns and whatever join type necessary. 

Additionally, data can be appended from one file to the other.

When the columns are chosen, ensure you are:
* Choosing the correct data type for that column
* Lining up the ordering of the columns from the drop-downs on the bottom half of the screen so both files match each other.
* Choosing the correct join type, the safe bet for testing purposes is always a left/right join.

![Report Merge Image](screenshots/ReportMerge-small.png?raw=true "Report Merge")

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See Instructions for how to deploy the project on a live system.

## Repository
[genius-bot](https://github.com/Knucklessg1/genius-bot.git)

#### Build Instructions
Build Python Package

```bash
sudo chmod +x ./*.py
pip install .
python setup.py bdist_wheel --universal
# Test Pypi
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# Prod Pypi
twine upload dist/*
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
Please attribute any uses to this repository. Do not resale this application. Test
All credits to the FFMPEG team for the audio/video conversions
## Authors

* **Audel Rouhi** - *Software & Automation Engineer + Data Scientist* - [knucklessg1](https://github.com/Knucklessg1)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## Acknowledgments
