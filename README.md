# Geniusbot 
*Version: 2.1.7*

![Geniusbot](geniusbot/img/geniusbot-small.png?raw=true "Geniusbot") 

The Ever-learning and ever-improving tool!
- Geniusbot Chat
- Media Download
- Website Screenshot
- Subtitle Shift
- Media Manager

#### Geniusbot Chat
Chat with your friendly Geniusbot. 

Powered by Artificial Intelligence scaled to your PC's performance!

![Geniusbot Chat](screenshots/geniusbot_home.png?raw=true "Geniusbot Chat")

#### Video Download
Download any YouTube, Twitter, or Rumble video(s) as MP3 or Webm/MP4 in a few different qualities. 
![Video Download](screenshots/geniusbot_video.png?raw=true "Video Download")

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

![Web Archiver](screenshots/geniusbot_website_archive.png?raw=true "Web Archiver")

#### Subtitle Shift
Shift a subtitle forward or backward a few seconds so it aligns with your video!

![Subtitle Shift](screenshots/geniusbot_shift_subtitles.png?raw=true "Subtitle Shift")

#### Media Downloader
Download videos from various websites! 

Supports: 

- YouTube
- DailyMotion
- Rumble
- Twitter
- BitChute
- And More!

![Media Downloader](screenshots/geniusbot_media_downloader.png?raw=true "Media Downloader")

#### Media Manager

Manage your media library by:
- Cleaning up names of files and folders based off pre-built filters. 
- Apply subtitles located in "Sub" folder within each media directory
- Move files to final destination after processing

![Subtitle Shift](screenshots/geniusbot_shift_subtitles.png?raw=true "Subtitle Shift")


## Install
```bash
pip install geniusbot
```

## Development Environment
```bash
bash ./build_container.sh
```

## Build Instructions
Build Python Package

```bash
sudo chmod +x ./*.py
pip install .
python setup.py bdist_wheel --universal
# Test Pypi
twine upload --repository-url https://test.pypi.org/legacy/ dist/* --verbose -u "Username" -p "Password"
# Prod Pypi
twine upload dist/* --verbose -u "Username" -p "Password"
```

## Repository
[geniusbot](https://github.com/Knucklessg1/geniusbot.git)

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
Huggingface Models
