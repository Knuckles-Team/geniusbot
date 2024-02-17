# Geniusbot

![PyPI - Version](https://img.shields.io/pypi/v/geniusbot)
![PyPI - Downloads](https://img.shields.io/pypi/dd/geniusbot)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/geniusbot)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/geniusbot)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/geniusbot)
![PyPI - License](https://img.shields.io/pypi/l/geniusbot)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/geniusbot)

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/geniusbot)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/geniusbot)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/geniusbot)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/geniusbot)

![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/geniusbot)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/geniusbot)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/geniusbot)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/geniusbot)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/geniusbot)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/geniusbot)


*Version: 3.29.1*

![Geniusbot](https://raw.githubusercontent.com/Knuckles-Team/geniusbot/master/geniusbot/img/geniusbot-small.png "Geniusbot")

The Ever-learning and ever-improving tool!

Click the arrows on the left of each of the items below to see more information about them.

<hr>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Geniusbot Chat </b></summary>
<br>
Chat with your friendly and extremely intelligent Geniusbot. 

Powered by Artificial Intelligence scaled to your PC's performance!

![Geniusbot Chat](https://raw.githubusercontent.com/Knuckles-Team/geniusbot/master/screenshots/geniusbot_home.png "Geniusbot Chat")

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

![User Entry Image](https://raw.githubusercontent.com/Knuckles-Team/geniusbot/master/screenshots/user.png "User Entry")

![Channel Entry Image](https://raw.githubusercontent.com/Knuckles-Team/geniusbot/master/screenshots/channel.png "Channel Entry")

Open File allows you to browse for a text file that has a list of YouTube links.
Examples contents:
```
https://www.youtube.com/watch?v=75-siCngYCc
https://www.youtube.com/watch?v=7RSpZkIjK4w
https://www.youtube.com/watch?v=7qRSAUb96wg
```

![Media Downloader](https://raw.githubusercontent.com/Knuckles-Team/geniusbot/master/screenshots/geniusbot_media_downloader.png "Media Downloader")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Media Manager </b></summary>
<br>
Manage your media library by:
- Cleaning up names of files and folders based off pre-built filters. 
- Apply subtitles located in "Sub" folder within each media directory
- Move files to final destination after processing

Download as MP3 or MP4

![Media Manager](https://raw.githubusercontent.com/Knuckles-Team/geniusbot/master/screenshots/geniusbot_media_manager.png "Media Manager")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Website Archiving </b></summary>
<br>
Archive any website by taking screenshots of any website entered or scraping that site for specific file types.

Choose from a variety of options like file type, quality, and image size.

![Web Archiver](https://raw.githubusercontent.com/Knuckles-Team/geniusbot/master/screenshots/geniusbot_website_archive.png "Web Archiver")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Subtitle Shift </b></summary>
<br>
Shift a subtitle forward or backward a few seconds so it aligns with your video!

![Subtitle Shift](https://raw.githubusercontent.com/Knuckles-Team/geniusbot/master/screenshots/geniusbot_shift_subtitles.png "Subtitle Shift")

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

![Report Manager](https://raw.githubusercontent.com/Knuckles-Team/geniusbot/master/screenshots/geniusbot_report_manager.png "Report Manager")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Repository Manager </b></summary>
<br>
Manage your repositories by cloning, pulling, or running your own set of git commands on a given directory

![Repository Manager](https://raw.githubusercontent.com/Knuckles-Team/geniusbot/master/screenshots/geniusbot_repository_manager.png "Repository Manager")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Rom Manager </b></summary>
<br>
Convert Game ROMs to Compressed Hunks of Data (CHD) file format or RVZ file format

Automatically generate missing .cue files for your .bin files!
![Rom Manager](https://raw.githubusercontent.com/Knuckles-Team/geniusbot/master/screenshots/geniusbot_rom_manager.png "Rom Manager")

</details>

<details >
<summary style="text-align:left; font-size:111%; color:black;"><b> Systems Manager </b></summary>
<br>
Manage your Linux/Windows System!

* Install Applications
* Clean
* Update
* Upgrade Geniusbot
* Enable Windows Features

</details>

<hr>


<details >
<summary style="text-align:left; font-size:130%; color:black;"><b> Install </b></summary>

```bash
pip install geniusbot
```

</details>

<details >
<summary style="text-align:left; font-size:130%; color:black;"><b> Build Executable </b></summary>

```bash
python -m pip install --upgrade pyinstaller
git clone https://github.com/Knuckles-Team/geniusbot.git
cd geniusbot
python -m venv .venv
./.venv/Scripts/activate

pyinstaller --name geniusbot --onefile --windowed --icon='./geniusbot/img/geniusbot.ico' --paths ./.venv/Lib/site-packages --hidden-import=appdirs --hidden-import=sklearn --hidden-import=sklearn.utils --hidden-import=nltk --hidden-import=gpt4all ./geniusbot/geniusbot.py
```

</details>

<details >
<summary style="text-align:left; font-size:130%; color:black;"><b> Build Setup Executable </b></summary>

```bash

```

</details>
<details>
  <summary style="text-align:left; font-size:130%; color:black;"><b>Repository Owners:</b></summary>


<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)
![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)
</details>
