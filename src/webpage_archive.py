import urllib.error
import urllib.parse
import urllib.request
import time
import os

from io import BytesIO

from PIL import Image
from Screenshot import Screenshot_Clipping #https://github.com/PyWizards/Selenium_Screenshot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class WebPageArchive:
    driver = None
    screenshotter = None
    DEFAULT_IMAGE_FORMAT = 'JPEG'
    DEFAULT_IMAGE_QUALITY = 80

    HIDDEN_SCROLL_BAR = 'hidden'
    DEFAULT_SCROLL_BAR = 'visible'

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

    def read_url(self, url):
        #url = 'https://prepareforchange.net/2020/03/27/benjamin-fulford-cobra-return-critical-corona-virus-and-war-updates/'
        self.driver.get(url)
        '''
        response = urllib.request.urlopen(url)
        webContent = response.read()
        f = open('test.html', 'wb')
        f.write(webContent)'''



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

    def save_webpage(self, url, file_name, hide_scrollbar=True, **kwargs):
        """
        :param driver: selenium driver object
        :param file_name:
        :param hide_scrollbar:
        :param kwargs: keywords parameters to pillow save function
        :type file_name: str
        :return: name of file
        """
        #define driver locally and navigate to URL
        driver = self.driver
        driver.get(url)
        # define necessary image properties
        image_options = dict()
        image_options['format'] = kwargs.get('format') or self.DEFAULT_IMAGE_FORMAT
        image_options['quality'] = kwargs.get('quality') or self.DEFAULT_IMAGE_QUALITY

        device_pixel_ratio = self.get_device_pixel_ratio(driver)

        # if device_pixel_ratio > 1:
        #     resize_window(driver, device_pixel_ratio)

        initial_offset = self.get_y_offset(driver)
        inner_height = self.get_inner_height(driver)
        scroll_height = self.get_scroll_height(driver)
        actual_page_size = scroll_height * device_pixel_ratio

        if hide_scrollbar:
            self.set_scrollbar(driver, self.HIDDEN_SCROLL_BAR)

        slices = self.make_screen_slices(driver, inner_height, scroll_height)

        self.glue_slices_into_image(slices, file_name, image_options, actual_page_size, device_pixel_ratio, inner_height,
                               scroll_height)

        # state of driver after script should to be the same as before
        if hide_scrollbar:
            self.set_scrollbar(driver, self.DEFAULT_SCROLL_BAR)

        if initial_offset != self.get_y_offset(driver):
            self.scroll_to(driver, initial_offset)

        return file_name

    def get_y_offset(self, driver):
        y_offset_js = 'return window.pageYOffset;'
        return driver.execute_script(y_offset_js)

    def glue_slices_into_image(self, slices, file_name, image_options, actual_page_size, device_pixel_ratio, inner_height, scroll_height):
        print('float ', actual_page_size)
        image_file = Image.new('RGB', (slices[0].size[0], actual_page_size))

        for i, img in enumerate(slices[:-1]):
            image_file.paste(img, (0, i * inner_height * device_pixel_ratio))
        else:
            image_file.paste(slices[-1], (0, (scroll_height - inner_height) * device_pixel_ratio))

        image_file.save(file_name, **image_options)

    def make_screen_slices(self, driver, inner_height, scroll_height):
        slices = []

        for offset in range(0, scroll_height + 1, inner_height):
            self.scroll_to(driver, offset)
            img = Image.open(BytesIO(driver.get_screenshot_as_png()))
            slices.append(img)

        return slices

    def get_scroll_height(self, driver):
        scroll_height_js = 'return document.body.scrollHeight;'
        return driver.execute_script(scroll_height_js)

    def get_inner_height(self, driver):
        inner_height_js = 'return window.innerHeight;'
        return driver.execute_script(inner_height_js)

    def get_device_pixel_ratio(self, driver):
        device_pixel_ratio_js = 'return window.devicePixelRatio;'
        return driver.execute_script(device_pixel_ratio_js)

    def set_scrollbar(self, driver, style):
        scrollbar_js = 'document.documentElement.style.overflow = \"{}\"'.format(style)
        driver.execute_script(scrollbar_js)

    def scroll_to(self, driver, offset):
        scroll_to_js = 'window.scrollTo(0, {});'
        driver.execute_script(scroll_to_js.format(offset))

    def resize_window(self, driver, device_pixel_ratio):
        old_width = driver.get_window_size()['width']
        old_height = driver.get_window_size()['height']
        driver.set_window_size(old_width // device_pixel_ratio, old_height // device_pixel_ratio)



test = WebPageArchive()
#test.fullpage_screenshot('https://waveguide.blog/tesla-hairpin-circuit-stout-copper-bars-replication/', r'.')
test.save_webpage('https://waveguide.blog/tesla-hairpin-circuit-stout-copper-bars-replication/', 'TEST_Q')
test.quit_driver()
#test.test_fullpage_screenshot()
