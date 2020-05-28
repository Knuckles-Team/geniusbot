import urllib.error
import urllib.parse
import urllib.request
import time
import os
import math
import re
import pandas as pd

from io import BytesIO

from PIL import Image

from twitter_scraper import get_tweets
# from Screenshot import Screenshot_Clipping #https://github.com/PyWizards/Selenium_Screenshot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

class WebPageArchive:
    SAVE_PATH = None
    OS_SAVE_PATH = None
    driver = None
    driver_path = None
    capabilities = None
    chrome_options = webdriver.ChromeOptions()
    # screenshotter = None
    DEFAULT_IMAGE_FORMAT = 'JPEG'
    DEFAULT_IMAGE_QUALITY = 80
    urls = []
    twitter_urls = []
    twitter_df = None
    log = None
    HIDDEN_SCROLL_BAR = 'hidden'
    DEFAULT_SCROLL_BAR = 'visible'

    def __init__(self, logger=None):
        print("test")
        if logger:
            self.log = logger
        else:
            self.log = None # Replace with log call in logger class
        self.log.info("Initializing Web Archive Complete!")
        self.capabilities = {
            'self.browserName': 'chrome',
            'chromeOptions': {
                'useAutomationExtension': False,
                'forceDevToolsScreenshot': True,
                'args': ['--start-maximized',
                         '--disable-infobars',
                         '--headless',
                         '--disable-gpu',
                         '--disable-notifications',
                         '--disable-extensions']
            }
        }

        # Pass the argument 1 to allow and 2 to block
        self.chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2
        })
        # Add Ublock Origin to Chrome
        self.chrome_options.add_extension('../lib/uBlock-Origin_v1.26.0.crx.crx')
        # self.screenshotter = Screenshot_Clipping.Screenshot()
        self.driver_path = f'{os.pardir}/lib/chromedriver83.exe'
        # driver_path = '.\chromedriver80.exe'
        print("Driver Path: ", self.driver_path)
        #self.launch_browser()

    def launch_browser(self):
        self.driver = webdriver.Chrome(executable_path=self.driver_path,
                                       desired_capabilities=self.capabilities,
                                       chrome_options=self.chrome_options)
        #self.driver.fullscreen_window()

    def append_link(self, url):
        print("URL Appended: ", url)
        self.urls.append(url)
        self.urls = list(dict.fromkeys(self.urls))

    def get_links(self):
        return self.urls

    def reset_links(self):
        print("Links Reset")
        self.urls = []

    def twitter_archiver(self, search, export=True, filename="twitter_export", filetype='csv', screenshot=False,
                         pages=None):
        self.twitter_df = pd.DataFrame()
        counter = 0
        if screenshot:
            self.launch_browser()
        if pages:
            for tweet in get_tweets(search, pages=pages):
                df_tmp = pd.DataFrame.from_dict(tweet)
                if screenshot:
                    self.twitter_urls.append(f"https://twitter.com{tweet['tweetUrl']}")
                    print("URL: ", f"https://twitter.com{tweet['tweetUrl']}")
                    self.screenshot(f"https://twitter.com{tweet['tweetUrl']}", filename=f'{filename}_{counter}')
                # df_tmp = df_tmp.T
                print(df_tmp)
                self.twitter_df = self.twitter_df.append(df_tmp, ignore_index=True)
                # print(tweet['text'])
                counter += 1
        else:
            for tweet in get_tweets(search):
                df_tmp = pd.DataFrame.from_dict(tweet)
                if screenshot:
                    self.twitter_urls.append(f"https://twitter.com{tweet['tweetUrl']}")
                    self.screenshot(f"https://twitter.com{tweet['tweetUrl']}", filename=f'{filename}_{counter}')
                # df_tmp = df_tmp.T
                print(df_tmp)
                self.twitter_df = self.twitter_df.append(df_tmp, ignore_index=True)
                # print(tweet['text'])
                counter += 1
        if screenshot:
            self.quit_driver()
        self.twitter_df = self.twitter_df.drop_duplicates(['tweetId'], keep='last')
        if export:
            self.twitter_df.to_csv(f"./{filename}.{filetype}", index=False)

    def read_url(self, url):
        # url = 'https://prepareforchange.net/2020/03/27/benjamin-fulford-cobra-return-critical-corona-virus-and-war-updates/'
        self.driver.fullscreen_window()
        self.driver.get(url)
        self.driver.execute_script('return document.readyState;')
        # Tries to Remove any alerts that may appear on the page
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present(),
                                                'Timed out waiting for any notification alerts')
            alert = self.driver.switch_to.alert
            alert.accept()
            print("alert accepted")
        except TimeoutException:
            print("no alert")
        # Tries to remove any persistent scrolling headers
        try:
            # Removes Any Fixed Elements
            self.driver.execute_script("""(function () { 
              var i, elements = document.querySelectorAll('body *');
            
              for (i = 0; i < elements.length; i++) {
                if (getComputedStyle(elements[i]).position === 'fixed') {
                  elements[i].parentNode.removeChild(elements[i]);
                }
              }
            })();""")

            '''self.driver.execute_script(
                'javascript:(function(){x=document.querySelectorAll("*");for(i=0;i<x.length;i++){elementStyle=getComputedStyle(x[i]);if(elementStyle.position=="fixed"||elementStyle.position=="sticky"){x[i].style.position="absolute";}}}())')

            fixed_nav = self.driver.execute_script("document.getElementsByClassName('residential-header sticky-header fixed')[0].classList.remove('fixed');")
            self.driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", fixed_nav)
            topnav = self.driver.find_element_by_id("topnav")
            self.driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", topnav)
            self.driver.execute_script("document.getElementById('topnav').setAttribute('style', 'position: absolute; top: 0px;');")'''
            print("ABLE TO REMOVE HEADER TOP BAR")
        except Exception as e:
            print(e)

    def screenshot(self, url, filename=None, filetype=DEFAULT_IMAGE_FORMAT, quality=DEFAULT_IMAGE_QUALITY):
        self.read_url(url)
        if filename:
            title = re.sub('[\\/:"*?<>|]', '', filename)
            self.save_webpage(f'{title}.{filetype}', hide_scrollbar=True)
        else:
            title = re.sub('[\\/:"*?<>|]', '', self.driver.title)
            title = title.replace(" ", "_")
            print("Title: ", title)
            self.save_webpage(f'{title}.{filetype}', hide_scrollbar=True)

    def fullpage_screenshot(self, url, filename=None, filetype=DEFAULT_IMAGE_FORMAT, quality=DEFAULT_IMAGE_QUALITY):
        self.read_url(url)
        if filename:
            title = re.sub('[\\/:"*?<>|.,]', '', filename)
            self.save_webpage(f'{title}.{filetype}', hide_scrollbar=True, format=filetype, quality=quality)
        else:
            title = re.sub('[\\/:"*?<>|.,]', '', self.driver.title)
            title = title.replace(" ", "_")
            print("Title: ", title)
            self.save_webpage(f'{title}.{filetype}', hide_scrollbar=True, format=filetype, quality=quality)

    def set_save_path(self, save_path):
        self.SAVE_PATH = save_path
        self.SAVE_PATH = self.SAVE_PATH.replace(os.sep, '/')
        self.set_os_save_path()

    def set_os_save_path(self):
        self.OS_SAVE_PATH = self.SAVE_PATH.replace('/', os.sep)

    def quit_driver(self):
        print("Chrome Driver Closed")
        self.driver.quit()

    def save_webpage(self, file_name, hide_scrollbar=True, **kwargs):
        # define necessary image properties
        image_options = dict()
        image_options['format'] = kwargs.get('format') or self.DEFAULT_IMAGE_FORMAT
        image_options['quality'] = kwargs.get('quality') or self.DEFAULT_IMAGE_QUALITY

        device_pixel_ratio = self.get_device_pixel_ratio()
        # print("Pixel Ratio: ", device_pixel_ratio)
        # if device_pixel_ratio > 1:
        #     resize_window(driver, device_pixel_ratio)

        initial_offset = self.get_y_offset()
        inner_height = self.get_inner_height()
        scroll_height = self.get_scroll_height()
        # print("Scroll Height: ", scroll_height)
        actual_page_size = math.ceil(scroll_height * device_pixel_ratio)

        if hide_scrollbar:
            self.set_scrollbar(self.HIDDEN_SCROLL_BAR)

        slices = self.make_screen_slices(inner_height, scroll_height)

        self.glue_slices_into_image(slices, file_name, image_options, actual_page_size, device_pixel_ratio,
                                    inner_height,
                                    scroll_height)

        # state of driver after script should to be the same as before
        if hide_scrollbar:
            self.set_scrollbar(self.DEFAULT_SCROLL_BAR)

        if initial_offset != self.get_y_offset():
            self.scroll_to(initial_offset)

        return file_name

    def get_y_offset(self):
        y_offset_js = 'return window.pageYOffset;'
        return self.driver.execute_script(y_offset_js)

    def glue_slices_into_image(self, slices, file_name, image_options, actual_page_size, device_pixel_ratio,
                               inner_height, scroll_height):
        '''stitched_image = Image.new('RGB', (slices[0].size[0], actual_page_size))
        x_offset = 0
        y_offset = 0
        for img in slices:
            stitched_image.paste(img, (x_offset, y_offset))
            y_offset += img.size[1]
        stitched_image.save(file_name, **image_options)
        '''
        image_file = Image.new('RGB', (slices[0].size[0], actual_page_size))
        for i, img in enumerate(slices[:-1]):
            image_file.paste(img, (0, math.ceil(i * inner_height * device_pixel_ratio)))
        else:
            image_file.paste(slices[-1], (0, math.ceil((scroll_height - inner_height) * device_pixel_ratio)))
        image_file.save(f'{self.SAVE_PATH}/{file_name}', **image_options)

    def make_screen_slices(self, inner_height, scroll_height):
        slices = []
        for offset in range(0, scroll_height + 1, inner_height):
            self.scroll_to(offset)
            try:
                # Removes Any Fixed Elements
                self.driver.execute_script("""(function () { 
                  var i, elements = document.querySelectorAll('body *');

                  for (i = 0; i < elements.length; i++) {
                    if (getComputedStyle(elements[i]).position === 'fixed') {
                      elements[i].parentNode.removeChild(elements[i]);
                    }
                  }
                })();""")
            except Exception as e:
                print(e)
            img = Image.open(BytesIO(self.driver.get_screenshot_as_png()))
            slices.append(img)
        return slices

    def get_scroll_height(self):
        scroll_height_js = 'return document.body.scrollHeight;'
        return self.driver.execute_script(scroll_height_js)

    def get_inner_height(self):
        inner_height_js = 'return window.innerHeight;'
        return self.driver.execute_script(inner_height_js)

    def get_device_pixel_ratio(self):
        device_pixel_ratio_js = 'return window.devicePixelRatio;'
        return self.driver.execute_script(device_pixel_ratio_js)

    def set_scrollbar(self, style):
        scrollbar_js = 'document.documentElement.style.overflow = \"{}\"'.format(style)
        self.driver.execute_script(scrollbar_js)

    def scroll_to(self, offset):
        scroll_to_js = 'window.scrollTo(0, {});'
        self.driver.execute_script(scroll_to_js.format(offset))

    def resize_window(self, device_pixel_ratio):
        old_width = self.driver.get_window_size()['width']
        old_height = self.driver.get_window_size()['height']
        self.driver.set_window_size(old_width // device_pixel_ratio, old_height // device_pixel_ratio)


'''
test = WebPageArchive()
test.twitter_archiver("realdonaldtrump", export=True, filename="twitter_export", filetype="csv", screenshot=True, pages=1)
'''
# test.twitter_archiver("realdonaldtrump", filename="twitter_export", filetype="csv", screenshot=False, pages=1)
'''
test = WebPageArchive()
test.launch_browser()
test.fullpage_screenshot('https://www.geeksforgeeks.org/how-to-get-title-of-a-webpage-using-selenium-in-python/')
test.quit_driver()
'''
# test.read_url('https://waveguide.blog/tesla-hairpin-circuit-stout-copper-bars-replication/')
# test.save_webpage('https://waveguide.blog/tesla-hairpin-circuit-stout-copper-bars-replication/', 'TEST_Q')
# test.test_fullpage_screenshot()
