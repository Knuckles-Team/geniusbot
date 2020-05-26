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