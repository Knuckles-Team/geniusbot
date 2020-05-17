import urllib.error
import urllib.parse
import urllib.request
import time
import os
import math
import re

from io import BytesIO

from PIL import Image
#from Screenshot import Screenshot_Clipping #https://github.com/PyWizards/Selenium_Screenshot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class WebPageArchive:
    driver = None
    driver_path = None
    capabilities = None
    #screenshotter = None
    DEFAULT_IMAGE_FORMAT = 'JPEG'
    DEFAULT_IMAGE_QUALITY = 80

    HIDDEN_SCROLL_BAR = 'hidden'
    DEFAULT_SCROLL_BAR = 'visible'

    def __init__(self):
        print("test")
        self.capabilities = {
           'self.browserName': 'chrome',
           'chromeOptions':  {
           'useAutomationExtension': False,
           'forceDevToolsScreenshot': True,
           'args': ['--start-maximized', '--disable-infobars', '--headless', '--disable-gpu']
           }
        }
        #self.screenshotter = Screenshot_Clipping.Screenshot()
        self.driver_path = f'{os.pardir}/lib/chromedriver80.exe'
        #driver_path = '.\chromedriver80.exe'
        print("Driver Path: ", self.driver_path)

    def launch_browser(self):
        self.driver = webdriver.Chrome(self.driver_path, desired_capabilities=self.capabilities)
        self.driver.fullscreen_window()

    def archive(self):
        driver = webdriver.Firefox()
        # driver = webdriver.Chrome('./chromedriver')
        driver.fullscreen_window()
        driver.get('http://www.google.com/')
        save_me = ActionChains(driver).key_down(Keys.CONTROL).key_down('s').key_up(Keys.CONTROL).key_up('s')
        print("Saved Button Found")
        save_me.perform()
        print("Saved Button Clicked")

    def read_url(self, url):
        #url = 'https://prepareforchange.net/2020/03/27/benjamin-fulford-cobra-return-critical-corona-virus-and-war-updates/'
        self.driver.fullscreen_window()
        self.driver.get(url)

    def screenshot(self, url, filename=None, filetype="png"):
        self.read_url(url)
        if filename:
            title = re.sub('[\\/:"*?<>|]', '', filename)
            self.save_webpage(f'{title}.{filetype}', hide_scrollbar=True)
        else:
            title = re.sub('[\\/:"*?<>|]', '', self.driver.title)
            title = title.replace(" ", "_")
            print("Title: ", title)
            self.save_webpage(f'{title}.{filetype}', hide_scrollbar=True)

    def fullpage_screenshot(self, url, filename=None, filetype="png"):
        self.read_url(url)
        if filename:
            title = re.sub('[\\/:"*?<>|]', '', filename)
            self.save_webpage(f'{title}.{filetype}', hide_scrollbar=True)
        else:
            title = re.sub('[\\/:"*?<>|]', '', self.driver.title)
            title = title.replace(" ", "_")
            print("Title: ", title)
            self.save_webpage(f'{title}.{filetype}', hide_scrollbar=True)

    def quit_driver(self):
        self.driver.quit()

    def save_webpage(self, file_name, hide_scrollbar=True, **kwargs):
        """
        :param driver: selenium driver object
        :param file_name:
        :param hide_scrollbar:
        :param kwargs: keywords parameters to pillow save function
        :type file_name: str
        :return: name of file
        """
        # define necessary image properties
        image_options = dict()
        image_options['format'] = kwargs.get('format') or self.DEFAULT_IMAGE_FORMAT
        image_options['quality'] = kwargs.get('quality') or self.DEFAULT_IMAGE_QUALITY

        device_pixel_ratio = self.get_device_pixel_ratio()
        #print("Pixel Ratio: ", device_pixel_ratio)
        # if device_pixel_ratio > 1:
        #     resize_window(driver, device_pixel_ratio)

        initial_offset = self.get_y_offset()
        inner_height = self.get_inner_height()
        scroll_height = self.get_scroll_height()
        #print("Scroll Height: ", scroll_height)
        actual_page_size = math.ceil(scroll_height * device_pixel_ratio)

        if hide_scrollbar:
            self.set_scrollbar(self.HIDDEN_SCROLL_BAR)

        slices = self.make_screen_slices(inner_height, scroll_height)

        self.glue_slices_into_image(slices, file_name, image_options, actual_page_size, device_pixel_ratio, inner_height,
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

    def glue_slices_into_image(self, slices, file_name, image_options, actual_page_size, device_pixel_ratio, inner_height, scroll_height):
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
        image_file.save(file_name, **image_options)

    def make_screen_slices(self, inner_height, scroll_height):
        slices = []
        for offset in range(0, scroll_height + 1, inner_height):
            self.scroll_to(offset)
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
test.launch_browser()
test.fullpage_screenshot('https://www.geeksforgeeks.org/how-to-get-title-of-a-webpage-using-selenium-in-python/')
test.quit_driver()
'''
#test.read_url('https://waveguide.blog/tesla-hairpin-circuit-stout-copper-bars-replication/')
#test.save_webpage('https://waveguide.blog/tesla-hairpin-circuit-stout-copper-bars-replication/', 'TEST_Q')
#test.test_fullpage_screenshot()
