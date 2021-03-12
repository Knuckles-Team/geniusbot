#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import getopt
import fileinput
import time
import os
import math
import re
import pandas as pd

from io import BytesIO

from PIL import Image, ImageChops
import piexif

from twitter_scraper import get_tweets
from selenium import webdriver
from log import Log
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException


class WebPageArchive:
    if os.name == 'nt':
        SAVE_PATH = f'C:\\Users\\{os.getlogin()}\\Downloads'
    else:
        home = os.path.expanduser("~")
        SAVE_PATH = os.path.join(home, "Downloads")
    OS_SAVE_PATH = SAVE_PATH
    driver = []
    capabilities = None
    chrome_options = webdriver.ChromeOptions()
    # screenshotter = None
    DEFAULT_IMAGE_FORMAT = 'PNG'
    DEFAULT_IMAGE_QUALITY = 80
    urls = []
    twitter_urls = []
    twitter_df = None
    log = None
    HIDDEN_SCROLL_BAR = 'hidden'
    DEFAULT_SCROLL_BAR = 'visible'
    screenshot_success = False
    screenshot_success_alt = False
    zoom_level = 100
    dpi = 1.0

    def __init__(self, logger=None):
        print("test")
        if logger:
            self.log = logger
        else:
            self.log = Log()
            self.log.init_logging()
        self.log.info("Initializing Web Archive Complete!")
        self.capabilities = {
            'self.browserName': 'chrome',
            'chromeOptions': {
                'useAutomationExtension': False,
                'forceDevToolsScreenshot': True
            }
        }
        # Pass the argument 1 to allow and 2 to block
        self.chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2
        })
        # Add Ublock Origin to Chrome
        adblock_path = f'{os.pardir}/lib/uBlock-Origin_v1.27.0.crx'
        if os.path.isfile(adblock_path):
            print("uBlock Origin Found")
        else:
            adblock_path = f'{os.curdir}/lib/uBlock-Origin_v1.27.0.crx'
        self.chrome_options.add_extension(adblock_path)
        # self.screenshotter = Screenshot_Clipping.Screenshot()
        # This option does not support opening with extensions. Comment it out.
        # self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument('--disable-notifications')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--dns-prefetch-disable')
        self.chrome_options.add_argument(f'--force-device-scale-factor={self.dpi}')
        self.chrome_options.add_argument(f'--high-dpi-support={self.dpi}')
        # This will now disable the extension I add so Comment it out
        # self.chrome_options.add_argument('--disable-extensions')

    def launch_browser(self, browser_count=None):
        try:
            self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                           desired_capabilities=self.capabilities,
                                           chrome_options=self.chrome_options)
            # for browser in browser_count:
            #    self.driver.append(webdriver.Chrome(executable_path=ChromeDriverManager().install(),
            #                               desired_capabilities=self.capabilities,
            #                               chrome_options=self.chrome_options))

        except Exception as e:
            print("Could not open with Latest Chrome Version", e)

    def open_file(self, file):
        webarchive_urls = open(file, 'r')
        for url in webarchive_urls:
            self.append_link(url)

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

    def set_zoom_level(self, zoom_percentage=100):
        print("Setting Zoom to: ", zoom_percentage)
        self.driver.execute_script(f"document.body.style.zoom='{zoom_percentage}%'")

    def save_zoom_level(self, zoom_percentage=100):
        self.zoom_level = zoom_percentage

    def save_dpi_level(self, dpi=1):
        self.dpi = dpi

    def read_url(self, url, zoom_percentage):
        # Comment out fullscreen_window, it will actually make it un-fullscreen
        # self.driver.fullscreen_window()
        try:
            self.driver.get(url)
            self.set_zoom_level(zoom_percentage)
            self.driver.execute_script('return document.readyState;')
        except Exception as e:
            print("Could not access website: ", e)
        # Tries to Remove any alerts that may appear on the page
        try:
            WebDriverWait(self.driver, 4).until(ec.alert_is_present(), 'Timed out waiting for any notification alerts')
            alert = self.driver.switch_to.alert
            alert.accept()
            print("alert accepted")
        except TimeoutException:
            print("no alert")
        time.sleep(1)
        # Tries to remove any persistent scrolling headers/fixed/sticky'd elements on the page
        inner_height = self.get_inner_height()
        scroll_height = self.get_scroll_height()
        self.remove_fixed_elements(inner_height, scroll_height)

    def clean_url(self):
        for url_index in range(0, len(self.urls)):
            self.urls[url_index] = re.sub('^chrome:.*$', '', self.urls[url_index])
            self.urls[url_index] = re.sub('^chrome-native:.*$', '', self.urls[url_index])
            self.urls[url_index] = re.sub('^.*facebook.*$', '', self.urls[url_index])
            self.urls[url_index] = re.sub('m.youtube', 'www.youtube', self.urls[url_index])
            self.urls[url_index] = re.sub('mobile.twitter', 'twitter', self.urls[url_index])
            self.urls[url_index] = re.sub('//m\.', 'www.', self.urls[url_index])
            self.urls[url_index] = self.urls[url_index].rstrip(os.linesep)
        try:
            self.urls.remove('\n')
        except ValueError:
            print("No Newlines Found")
        try:
            self.urls.remove('')
        except ValueError:
            print("No Empty Strings Found")

        self.urls = list(dict.fromkeys(filter(None, self.urls)))
        print(f'URLS #: {len(self.urls)}')
        for url_index in range(0, len(self.urls)):
            print(f'# {url_index} URL: {self.urls[url_index]}')

    def screenshot(self, url, zoom_percentage=100, filename=None, filetype=DEFAULT_IMAGE_FORMAT,
                   quality=DEFAULT_IMAGE_QUALITY):
        self.read_url(url, zoom_percentage)
        print("Quality: ", quality)
        self.set_scrollbar(self.HIDDEN_SCROLL_BAR)
        if filename:
            title = re.sub('[\\\\/:"*?<>|\']', '', filename)
            title = (title[:140]) if len(title) > 140 else title
            self.driver.save_screenshot(f'{self.SAVE_PATH}/{title}.{filetype}')
        else:
            print("driver title ", self.driver.title)
            print("Url, ", url)
            if self.driver.title:
                title = re.sub('[\\\\/:"*?<>|\']', '', self.driver.title)
                title = title.replace(" ", "_")
                title = (title[:140]) if len(title) > 140 else title
                print("Title: ", title)
                self.driver.save_screenshot(f'{self.SAVE_PATH}/{title}.{filetype}')
            else:
                title = re.sub('[\\\\/:"*?<>|.,\']', '', url)
                title = title.replace(" ", "_")
                title = (title[:140]) if len(title) > 140 else title
                print("Title: ", title)
                self.driver.save_screenshot(f'{self.SAVE_PATH}/{title}.{filetype}')

    def fullpage_screenshot(self, url, zoom_percentage=100, filename=None, filetype=DEFAULT_IMAGE_FORMAT,
                            quality=DEFAULT_IMAGE_QUALITY):
        self.read_url(url, zoom_percentage)
        if filename:
            title = re.sub('[\\\\/:"*?<>|.,\']', '', filename)
            title = (title[:140]) if len(title) > 140 else title
        else:
            print("driver title ", self.driver.title)
            print("Url, ", url)
            if self.driver.title:
                title = re.sub('[\\\\/:"*?<>|.,\']', '', self.driver.title)
                title = title.replace(" ", "_")
                title = (title[:140]) if len(title) > 140 else title
            else:
                title = re.sub('[\\\\/:"*?<>.,|\']', '', url)
                title = title.replace(" ", "_")
                title = (title[:140]) if len(title) > 140 else title
            print("Title: ", title)
        self.save_webpage(f'{title}.{filetype}', url=url, hide_scrollbar=True, format=filetype, quality=quality)
        if not self.screenshot_success:
            self.fullpage_screenshot_alternative(url=f'{url}', zoom_percentage=zoom_percentage, filename=f'{title}',
                                                 filetype=filetype, quality=quality)

    def fullpage_screenshot_alternative(self, url, zoom_percentage=100, filename=None, **kwargs):
        zeroth_ifd = {
            piexif.ImageIFD.Make: u"GeniusBot",
            # piexif.ImageIFD.XResolution: (96, 1),
            # piexif.ImageIFD.YResolution: (96, 1),
            piexif.ImageIFD.Software: u"GeniusBot",
            piexif.ImageIFD.ImageDescription: f"{url}".encode('utf-8'),
        }
        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: u"Today",
            piexif.ExifIFD.UserComment: f"{url}".encode('utf-8'),
            # piexif.ExifIFD.LensMake: u"LensMake",
            # piexif.ExifIFD.Sharpness: 65535,
            # piexif.ExifIFD.LensSpecification: ((1, 1), (1, 1), (1, 1), (1, 1)),
        }
        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            # piexif.GPSIFD.GPSAltitudeRef: 1,
            piexif.GPSIFD.GPSDateStamp: u"1999:99:99 99:99:99",
        }
        first_ifd = {
            piexif.ImageIFD.Make: u"GeniusBot",
            # piexif.ImageIFD.XResolution: (40, 1),
            # piexif.ImageIFD.YResolution: (40, 1),
            piexif.ImageIFD.Software: u"GeniusBot"
        }
        exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd, "1st": first_ifd}  # , "thumbnail": thumbnail}
        exif_bytes = piexif.dump(exif_dict)
        # define necessary image properties
        image_options = dict()
        # This will add the URL of the webite to the description
        image_options['exif'] = exif_bytes
        image_options['format'] = kwargs.get('format') or self.DEFAULT_IMAGE_FORMAT
        image_options['quality'] = kwargs.get('quality') or self.DEFAULT_IMAGE_QUALITY
        filetype = kwargs.get('format') or self.DEFAULT_IMAGE_FORMAT
        quality = kwargs.get('quality') or self.DEFAULT_IMAGE_QUALITY
        print("Attempting alternative screenshot method")
        self.driver.execute_script(f"window.scrollTo({0}, {0})")
        total_width = self.driver.execute_script("return document.body.offsetWidth")
        total_height = self.driver.execute_script("return document.body.parentNode.scrollHeight")
        viewport_width = self.driver.execute_script("return document.body.clientWidth")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        rectangles = []
        i = 0
        while i < total_height:
            ii = 0
            top_height = i + viewport_height
            if top_height > total_height:
                top_height = total_height
            while ii < total_width:
                top_width = ii + viewport_width
                if top_width > total_width:
                    top_width = total_width
                rectangles.append((ii, i, top_width, top_height))
                ii = ii + viewport_width
            i = i + viewport_height
        stitched_image = Image.new('RGB', (total_width, total_height))
        previous = None
        part = 0

        for rectangle in rectangles:
            if not previous is None:
                self.driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            file_name = "part_{0}.png".format(part)
            self.driver.get_screenshot_as_file(file_name)
            screenshot = Image.open(file_name)

            if rectangle[1] + viewport_height > total_height:
                offset = (rectangle[0], total_height - viewport_height)
            else:
                offset = (rectangle[0], rectangle[1])
            stitched_image.paste(screenshot, offset)
            del screenshot
            os.remove(file_name)
            part = part + 1
            previous = rectangle
        print(f"Saving image to: {self.SAVE_PATH}/{filename}.{filetype}'")
        stitched_image.save(f"{self.SAVE_PATH}/{filename}.{filetype}", **image_options)
        print("Finishing chrome full page screenshot workaround...")
        if not ImageChops.invert(stitched_image).getbbox() or not stitched_image.getbbox():
            print("Could not save full page screenshot, saving single page screenshot instead")
            self.screenshot(url=f'{url}', zoom_percentage=zoom_percentage, filename=filename, filetype=filetype,
                            quality=quality)

    def set_save_path(self, save_path):
        self.SAVE_PATH = save_path
        self.SAVE_PATH = self.SAVE_PATH.replace(os.sep, '/')
        self.set_os_save_path()

    def set_os_save_path(self):
        self.OS_SAVE_PATH = self.SAVE_PATH.replace('/', os.sep)

    def quit_driver(self):
        print("Chrome Driver Closed")
        self.driver.quit()

    def save_webpage(self, file_name, url="", hide_scrollbar=True, **kwargs):
        zeroth_ifd = {
            piexif.ImageIFD.Make: u"GeniusBot",
            # piexif.ImageIFD.XResolution: (96, 1),
            # piexif.ImageIFD.YResolution: (96, 1),
            piexif.ImageIFD.Software: u"GeniusBot",
            piexif.ImageIFD.ImageDescription: f"{url}".encode('utf-8'),
        }
        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: u"Today",
            piexif.ExifIFD.UserComment: f"{url}".encode('utf-8'),
            # piexif.ExifIFD.LensMake: u"LensMake",
            # piexif.ExifIFD.Sharpness: 65535,
            # piexif.ExifIFD.LensSpecification: ((1, 1), (1, 1), (1, 1), (1, 1)),
        }
        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            # piexif.GPSIFD.GPSAltitudeRef: 1,
            piexif.GPSIFD.GPSDateStamp: u"1999:99:99 99:99:99",
        }
        first_ifd = {
            piexif.ImageIFD.Make: u"GeniusBot",
            # piexif.ImageIFD.XResolution: (40, 1),
            # piexif.ImageIFD.YResolution: (40, 1),
            piexif.ImageIFD.Software: u"GeniusBot"
        }
        exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd, "1st": first_ifd}  # , "thumbnail": thumbnail}
        exif_bytes = piexif.dump(exif_dict)
        # define necessary image properties
        image_options = dict()
        # This will add the URL of the webite to the description
        image_options['exif'] = exif_bytes
        image_options['format'] = kwargs.get('format') or self.DEFAULT_IMAGE_FORMAT
        image_options['quality'] = kwargs.get('quality') or self.DEFAULT_IMAGE_QUALITY

        # Changes the ratio of the screen of the device.
        device_pixel_ratio = self.get_device_pixel_ratio()
        print("Pixel Ratio: ", device_pixel_ratio)
        if device_pixel_ratio > 1:
            self.resize_window(device_pixel_ratio)

        if hide_scrollbar:
            self.set_scrollbar(self.HIDDEN_SCROLL_BAR)

        inner_height = self.get_inner_height()
        scroll_height = self.get_scroll_height()
        initial_offset = self.get_y_offset()
        actual_page_size = math.ceil(scroll_height * device_pixel_ratio)

        # Screenshot all slices
        print("Making Screen Slices")
        slices = self.make_screen_slices(inner_height, scroll_height)
        print("Glueing Slices")
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
        image_file = Image.new('RGB', (slices[0].size[0], actual_page_size))
        for i, img in enumerate(slices[:-1]):
            image_file.paste(img, (0, math.ceil(i * inner_height * device_pixel_ratio)))
        else:
            image_file.paste(slices[-1], (0, math.ceil((scroll_height - inner_height) * device_pixel_ratio)))
        try:
            image_file.save(f'{self.SAVE_PATH}/{file_name}', **image_options)
            self.screenshot_success = True
        except Exception as e:
            print("Could not save image error: ", e)
            try:
                os.remove(f'{self.SAVE_PATH}/{file_name}')
            except Exception as e:
                print (f"Could not remove file, does it exist? {e}")
            self.screenshot_success = False

    def remove_fixed_elements(self, inner_height, scroll_height):
        for offset in range(0, scroll_height + 1, inner_height):
            self.scroll_to(offset)
            try:
                # Removes Any Fixed Elements
                self.driver.execute_script("""(function () { 
                  var i, elements = document.querySelectorAll('body *');

                  for (i = 0; i < elements.length; i++) {
                    if (getComputedStyle(elements[i]).position === 'fixed' || getComputedStyle(elements[i]).position === 'sticky' || getComputedStyle(elements[i]).position === '-webkit-sticky') {
                      elements[i].parentNode.removeChild(elements[i]);
                    }
                  }
                })();""")
            except Exception as e:
                print(e)

    def make_screen_slices(self, inner_height, scroll_height):
        slices = []
        for offset in range(0, scroll_height + 1, inner_height):
            self.scroll_to(offset)
            img = Image.open(BytesIO(self.driver.get_screenshot_as_png()))
            slices.append(img)
        return slices

    def get_scroll_height(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.driver.execute_script("window.scrollTo(0, 0)")
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


def main(argv):
    filename = "./links.txt"
    archive = WebPageArchive()
    clean_flag = False
    file_flag = False
    zoom_level = 100

    try:
        opts, args = getopt.getopt(argv, "hcd:f:l:t:z:", ["help", "clean", "directory", "dpi=", "file=", "links=", "type=",
                                                          "zoom="])
    except getopt.GetoptError:
        print('Usage:\npython3 webpage_archive.py -c -f <links_file.txt> -l "<link1,link2,link3>" -t <JPEG/PNG> -d ~/Downloads -z 150')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('Usage:\npython3 webpage_archive.py -c -f <links_file.txt> -l "<link1,link2,link3>" -t <JPEG/PNG> -d "~/Downloads" -z 150')
            sys.exit()
        elif opt in ("-c", "--clean"):
            clean_flag = True
        elif opt in ("-d", "--directory"):
            archive.set_save_path(arg)
        elif opt == "--dpi":
            archive.save_dpi_level(arg)
        elif opt in ("-f", "--file"):
            file_flag = True
            filename = arg
        elif opt in ("-l", "--links"):
            url_list = arg.split(",")
            for url in url_list:
                archive.append_link(url)
        elif opt in ("-t", "--type"):
            if arg == "PNG" or arg == "png" or arg == "JPG" or arg == "jpg" or arg == "JPEG" or arg == "jpeg":
                archive.DEFAULT_IMAGE_FORMAT = f'{arg}'
        elif opt in ("-z", "--zoom"):
            zoom_level = arg

    if file_flag:
        print(f"Opening File: {filename}")
        archive.open_file(filename)

    if clean_flag:
        print(f"Cleaning Links")
        archive.clean_url()

    archive.launch_browser()

    for url in archive.urls:
        archive.save_zoom_level(zoom_level)
        archive.fullpage_screenshot(url=f'{url}', zoom_percentage=zoom_level)
    archive.quit_driver()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Main Usage:\npython3 webpage_archive.py -c -f <links_file.txt> -l "<link1,link2,link3>" -t <JPEG/PNG> -d "~/Downloads" -z 100')
        sys.exit(2)
    main(sys.argv[1:])
