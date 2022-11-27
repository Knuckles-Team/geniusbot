# Geniusbot 
*Version: 3.3.0*

![Geniusbot](https://raw.githubusercontent.com/Knucklessg1/geniusbot/master/geniusbot/img/geniusbot-small.png "Geniusbot") 

The Ever-learning and ever-improving tool!

Click the arrows on the left of each of the items below to see more information about them.

<hr>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Geniusbot Chat </b></summary>
<br>
Chat with your friendly Geniusbot. 

Powered by Artificial Intelligence scaled to your PC's performance!

![Geniusbot Chat](https://raw.githubusercontent.com/Knucklessg1/geniusbot/master/screenshots/geniusbot_home.png "Geniusbot Chat")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Media Downloader </b></summary>
<br>
Download videos from various websites! 

Supports: 

- YouTube
- DailyMotion
- Rumble
- Twitter
- BitChute
- And More!

Examples for how to find user & channel.

![User Entry Image](https://raw.githubusercontent.com/Knucklessg1/geniusbot/master/screenshots/user.png "User Entry")

![Channel Entry Image](https://raw.githubusercontent.com/Knucklessg1/geniusbot/master/screenshots/channel.png "Channel Entry")

Open File allows you to browse for a text file that has a list of YouTube links.
Examples contents:
```
https://www.youtube.com/watch?v=75-siCngYCc
https://www.youtube.com/watch?v=7RSpZkIjK4w
https://www.youtube.com/watch?v=7qRSAUb96wg
```

![Media Downloader](https://raw.githubusercontent.com/Knucklessg1/geniusbot/master/screenshots/geniusbot_media_downloader.png "Media Downloader")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Media Manager </b></summary>
<br>
Manage your media library by:
- Cleaning up names of files and folders based off pre-built filters. 
- Apply subtitles located in "Sub" folder within each media directory
- Move files to final destination after processing

Download as MP3 or MP4

![Media Manager](https://raw.githubusercontent.com/Knucklessg1/geniusbot/master/screenshots/geniusbot_media_manager.png "Media Manager")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Website Archiving </b></summary>
<br>
Archive any website by taking screenshots of any website entered.

Choose from a variety of options like file type, quality, and image size.

![Web Archiver](https://raw.githubusercontent.com/Knucklessg1/geniusbot/master/screenshots/geniusbot_website_archive.png "Web Archiver")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Subtitle Shift </b></summary>
<br>
Shift a subtitle forward or backward a few seconds so it aligns with your video!

![Subtitle Shift](https://raw.githubusercontent.com/Knucklessg1/geniusbot/master/screenshots/geniusbot_shift_subtitles.png "Subtitle Shift")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Report Manager </b></summary>
<br>
Generate report analysis using:
- Visualization plots
- Pandas Profiling
- Report Analysis Text file

Merge reports with the following methods:
- Inner
- Outer
- Left
- Right
- Append

Multiple column selection optional for Inner, Outer, Left, and Right joining

![Report Manager](https://raw.githubusercontent.com/Knucklessg1/geniusbot/master/screenshots/geniusbot_report_manager.png "Report Manager")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Repository Manager </b></summary>
<br>
Manage your repositories by cloning, pulling, or running your own set of git commands on a given directory

![Repository Manager](https://raw.githubusercontent.com/Knucklessg1/geniusbot/master/screenshots/geniusbot_repository_manager.png "Repository Manager")

</details>

<hr>

### Install
```bash
pip install geniusbot
```

<details >
<summary style="text-align:left; font-size:130%; color:black;"><b> Build </b></summary>
<br>

### Development Environment
```bash
bash ./build_container.sh
```

#### Install Instructions
Install Python Package

```bash
python -m pip install geniusbot
```


### Build Instructions
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

</details>



### Repository
[geniusbot](https://github.com/Knucklessg1/geniusbot.git)

### Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

### License
Please attribute any uses to this repository. Do not resale this application. Test
All credits to the FFMPEG team for the audio/video conversions
### Authors

* **Audel Rouhi** - *Software & Automation Engineer + Data Scientist* - [knucklessg1](https://github.com/Knucklessg1)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

### Acknowledgments
Huggingface Models
