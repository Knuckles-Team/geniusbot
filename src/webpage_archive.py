import urllib.error
import urllib.parse
import urllib.request
import time
import os

from Screenshot import Screenshot_Clipping #https://github.com/PyWizards/Selenium_Screenshot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class WebPageArchive:
    driver = None
    screenshotter = None

    def __init__(self):
        print("test")
        capabilities = {
           'self.browserName': 'chrome',
           'chromeOptions':  {
           'useAutomationExtension': False,
           'forceDevToolsScreenshot': True,
           'args': ['--start-maximized', '--disable-infobars', '--headless']
           }
        }
        self.screenshotter = Screenshot_Clipping.Screenshot()
        driver_path = f'{os.pardir}/lib/chromedriver80.exe'
        #driver_path = '.\chromedriver80.exe'
        print("Driver Path: ", driver_path)
        self.driver = webdriver.Chrome(driver_path, desired_capabilities=capabilities)

    def archive(self):
        driver = webdriver.Firefox()
        # driver = webdriver.Chrome('./chromedriver')
        driver.fullscreen_window()
        driver.get('http://www.google.com/')
        save_me = ActionChains(driver).key_down(Keys.CONTROL).key_down('s').key_up(Keys.CONTROL).key_up('s')
        print("Saved Button Found")
        save_me.perform()
        print("Saved Button Clicked")

    def read_url(self):
        url = 'https://prepareforchange.net/2020/03/27/benjamin-fulford-cobra-return-critical-corona-virus-and-war-updates/'
        response = urllib.request.urlopen(url)
        webContent = response.read()
        f = open('test.html', 'wb')
        f.write(webContent)

    def screenshot(self, url, savepath):
        self.driver.fullscreen_window()
        url = url
        #the element with longest height on page
        self.driver.get(url)
        self.driver.save_screenshot(f"{savepath}/screenshot-regular.png")


    def fullpage_screenshot(self, url, savepath):
        self.driver.fullscreen_window()
        url = url
        #the element with longest height on page
        self.driver.get(url)
        img_url=self.screenshotter.full_Screenshot(self.driver, save_path=savepath, image_name='screenshot-full.png')
        print(img_url)

    def quit_driver(self):
        self.driver.close()
        self.driver.quit()

test = WebPageArchive()
test.fullpage_screenshot('https://waveguide.blog/tesla-hairpin-circuit-stout-copper-bars-replication/', r'.')
test.quit_driver()
#test.test_fullpage_screenshot()
