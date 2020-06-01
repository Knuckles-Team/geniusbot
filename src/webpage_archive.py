import urllib.error
import urllib.parse
import urllib.request
import time
import platform
import os
import math
import re
import pandas as pd

from io import BytesIO

from PIL import Image
import piexif

from twitter_scraper import get_tweets
# from Screenshot import Screenshot_Clipping #https://github.com/PyWizards/Selenium_Screenshot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


class WebPageArchive:
    SAVE_PATH = None
    OS_SAVE_PATH = None
    driver = None
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
                'forceDevToolsScreenshot': True
            }
        }
        # Pass the argument 1 to allow and 2 to block
        self.chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2
        })
        # Add Ublock Origin to Chrome
        self.chrome_options.add_extension('../lib/uBlock-Origin_v1.27.0.crx')
        # self.screenshotter = Screenshot_Clipping.Screenshot()
        # This option does not support opening with extensions. Comment it out.
        #self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument('--disable-notifications')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        # This will now disable the extension I add so Comment it out
        #self.chrome_options.add_argument('--disable-extensions')

    def launch_browser(self):
            try:
                # If not installed, run:
                # wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
                # sudo apt install ./google-chrome-stable_current_amd64.deb
                self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                                               desired_capabilities=self.capabilities,
                                               chrome_options=self.chrome_options)
            except Exception as e:
                print("Could not open with Latest Chrome Version", e)

    def append_link(self, url):
        print("URL Appended: ", url)
        self.urls.append(url)
        self.urls = list(dict.fromkeys(self.urls))

    def get_links(self):
        return self.urls

    def reset_links(self):
        print("Links Reset")
        self.urls = []

    def twitter_archiver(self, search, export=True, filename="twitter_export", filetype='csv', screenshot=False, pages=None):
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
        # Comment out fullscreen_window, it will actually make it un-fullscreen
        #self.driver.fullscreen_window()
        try:
            self.driver.get(url)
            self.driver.execute_script('return document.readyState;')
        except Exception as e:
            print("Could not access website: ", e)
        # Tries to Remove any alerts that may appear on the page
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present(),
                                                'Timed out waiting for any notification alerts')
            alert = self.driver.switch_to.alert
            alert.accept()
            print("alert accepted")
        except TimeoutException:
            print("no alert")

        # Tries to remove any persistent scrolling headers/fixed/sticky'd elements on the page
        inner_height = self.get_inner_height()
        scroll_height = self.get_scroll_height()
        self.remove_fixed_elements(inner_height, scroll_height)

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
            self.save_webpage(f'{title}.{filetype}', url=url, hide_scrollbar=True, format=filetype, quality=quality)
        else:
            title = re.sub('[\\/:"*?<>|.,]', '', self.driver.title)
            title = title.replace(" ", "_")
            print("Title: ", title)
            self.save_webpage(f'{title}.{filetype}', url=url, hide_scrollbar=True, format=filetype, quality=quality)

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
        '''
        11 = ProcessingSoftware
        18246 = Rating
        18249 = RatingPercent
        254 = NewSubfileType
        255 = SubfileType
        256 = ImageWidth
        257 = ImageLength
        258 = BitsPerSample
        259 = Compression
        262 = PhotometricInterpretation
        263 = Threshholding
        264 = CellWidth
        265 = CellLength
        266 = FillOrder
        269 = DocumentName
        270 = ImageDescription
        271 = Make
        272 = Model
        273 = StripOffsets
        274 = Orientation
        277 = SamplesPerPixel
        278 = RowsPerStrip
        279 = StripByteCounts
        282 = XResolution
        283 = YResolution
        284 = PlanarConfiguration
        290 = GrayResponseUnit
        291 = GrayResponseCurve
        292 = T4Options
        293 = T6Options
        296 = ResolutionUnit
        301 = TransferFunction
        305 = Software
        306 = DateTime
        315 = Artist
        316 = HostComputer
        317 = Predictor
        318 = WhitePoint
        319 = PrimaryChromaticities
        320 = ColorMap
        321 = HalftoneHints
        322 = TileWidth
        323 = TileLength
        324 = TileOffsets
        325 = TileByteCounts
        32781 = ImageID
        330 = SubIFDs
        332 = InkSet
        333 = InkNames
        334 = NumberOfInks
        33421 = CFARepeatPatternDim
        33422 = CFAPattern
        33423 = BatteryLevel
        33432 = Copyright
        33434 = ExposureTime
        336 = DotRange
        337 = TargetPrinter
        338 = ExtraSamples
        339 = SampleFormat
        340 = SMinSampleValue
        341 = SMaxSampleValue
        342 = TransferRange
        343 = ClipPath
        34377 = ImageResources
        344 = XClipPathUnits
        345 = YClipPathUnits
        346 = Indexed
        34665 = ExifTag
        34675 = InterColorProfile
        347 = JPEGTables
        34853 = GPSTag
        34857 = Interlace
        34858 = TimeZoneOffset
        34859 = SelfTimerMode
        351 = OPIProxy
        37387 = FlashEnergy
        37388 = SpatialFrequencyResponse
        37389 = Noise
        37390 = FocalPlaneXResolution
        37391 = FocalPlaneYResolution
        37392 = FocalPlaneResolutionUnit
        37393 = ImageNumber
        37394 = SecurityClassification
        37395 = ImageHistory
        37397 = ExposureIndex
        37398 = TIFFEPStandardID
        37399 = SensingMethod
        40091 = XPTitle
        40092 = XPComment
        40093 = XPAuthor
        40094 = XPKeywords
        40095 = XPSubject
        50341 = PrintImageMatching
        50706 = DNGVersion
        50707 = DNGBackwardVersion
        50708 = UniqueCameraModel
        50709 = LocalizedCameraModel
        50710 = CFAPlaneColor
        50711 = CFALayout
        50712 = LinearizationTable
        50713 = BlackLevelRepeatDim
        50714 = BlackLevel
        50715 = BlackLevelDeltaH
        50716 = BlackLevelDeltaV
        50717 = WhiteLevel
        50718 = DefaultScale
        50719 = DefaultCropOrigin
        50720 = DefaultCropSize
        50721 = ColorMatrix1
        50722 = ColorMatrix2
        50723 = CameraCalibration1
        50724 = CameraCalibration2
        50725 = ReductionMatrix1
        50726 = ReductionMatrix2
        50727 = AnalogBalance
        50728 = AsShotNeutral
        50729 = AsShotWhiteXY
        50730 = BaselineExposure
        50731 = BaselineNoise
        50732 = BaselineSharpness
        50733 = BayerGreenSplit
        50734 = LinearResponseLimit
        50735 = CameraSerialNumber
        50736 = LensInfo
        50737 = ChromaBlurRadius
        50738 = AntiAliasStrength
        50739 = ShadowScale
        50740 = DNGPrivateData
        50741 = MakerNoteSafety
        50778 = CalibrationIlluminant1
        50779 = CalibrationIlluminant2
        50780 = BestQualityScale
        50781 = RawDataUniqueID
        50827 = OriginalRawFileName
        50828 = OriginalRawFileData
        50829 = ActiveArea
        50830 = MaskedAreas
        50831 = AsShotICCProfile
        50832 = AsShotPreProfileMatrix
        50833 = CurrentICCProfile
        50834 = CurrentPreProfileMatrix
        50879 = ColorimetricReference
        50931 = CameraCalibrationSignature
        50932 = ProfileCalibrationSignature
        50934 = AsShotProfileName
        50935 = NoiseReductionApplied
        50936 = ProfileName
        50937 = ProfileHueSatMapDims
        50938 = ProfileHueSatMapData1
        50939 = ProfileHueSatMapData2
        50940 = ProfileToneCurve
        50941 = ProfileEmbedPolicy
        50942 = ProfileCopyright
        50964 = ForwardMatrix1
        50965 = ForwardMatrix2
        50966 = PreviewApplicationName
        50967 = PreviewApplicationVersion
        50968 = PreviewSettingsName
        50969 = PreviewSettingsDigest
        50970 = PreviewColorSpace
        50971 = PreviewDateTime
        50972 = RawImageDigest
        50973 = OriginalRawFileDigest
        50974 = SubTileBlockSize
        50975 = RowInterleaveFactor
        50981 = ProfileLookTableDims
        50982 = ProfileLookTableData
        51008 = OpcodeList1
        51009 = OpcodeList2
        51022 = OpcodeList3
        51041 = NoiseProfile
        512 = JPEGProc
        513 = JPEGInterchangeFormat
        514 = JPEGInterchangeFormatLength
        515 = JPEGRestartInterval
        517 = JPEGLosslessPredictors
        518 = JPEGPointTransforms
        519 = JPEGQTables
        520 = JPEGDCTables
        521 = JPEGACTables
        529 = YCbCrCoefficients
        530 = YCbCrSubSampling
        531 = YCbCrPositioning
        532 = ReferenceBlackWhite
        60606 = ZZZTestSlong1
        60607 = ZZZTestSlong2
        700 = XMLPacket
        '''
        zeroth_ifd = {
            piexif.ImageIFD.Make: u"GeniusBot",
            #piexif.ImageIFD.XResolution: (96, 1),
            #piexif.ImageIFD.YResolution: (96, 1),
            piexif.ImageIFD.Software: u"GeniusBot",
            piexif.ImageIFD.ImageDescription: f"{url}".encode('utf-8'),
        }
        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: u"Today",
            piexif.ExifIFD.UserComment: f"{url}".encode('utf-8'),
            #piexif.ExifIFD.LensMake: u"LensMake",
            #piexif.ExifIFD.Sharpness: 65535,
            #piexif.ExifIFD.LensSpecification: ((1, 1), (1, 1), (1, 1), (1, 1)),
        }
        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            #piexif.GPSIFD.GPSAltitudeRef: 1,
            piexif.GPSIFD.GPSDateStamp: u"1999:99:99 99:99:99",
        }
        first_ifd = {
            piexif.ImageIFD.Make: u"GeniusBot",
            #piexif.ImageIFD.XResolution: (40, 1),
            #piexif.ImageIFD.YResolution: (40, 1),
            piexif.ImageIFD.Software: u"GeniusBot"
        }
        exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd, "1st": first_ifd}#, "thumbnail": thumbnail}
        exif_bytes = piexif.dump(exif_dict)
        # define necessary image properties
        image_options = dict()
        # This will add the URL of the webite to the description
        image_options['exif'] = exif_bytes
        image_options['format'] = kwargs.get('format') or self.DEFAULT_IMAGE_FORMAT
        image_options['quality'] = kwargs.get('quality') or self.DEFAULT_IMAGE_QUALITY

        device_pixel_ratio = self.get_device_pixel_ratio()
        # print("Pixel Ratio: ", device_pixel_ratio)
        # if device_pixel_ratio > 1:
        #     resize_window(driver, device_pixel_ratio)

        inner_height = self.get_inner_height()
        scroll_height = self.get_scroll_height()
        print("Inner Scroll Height Before: ", inner_height)
        print("Scroll Height Before: ", scroll_height)
        if hide_scrollbar:
            self.set_scrollbar(self.HIDDEN_SCROLL_BAR)

        # Remove Sticky and Fixed Elements First
        #self.remove_fixed_elements(inner_height, scroll_height)
        print("Inner Scroll Height After: ", inner_height)
        print("Scroll Height After: ", scroll_height)
        # Get New Screensize after removing fixed elements
        device_pixel_ratio = self.get_device_pixel_ratio()
        initial_offset = self.get_y_offset()
        inner_height = self.get_inner_height()
        scroll_height = self.get_scroll_height()
        actual_page_size = math.ceil(scroll_height * device_pixel_ratio)

        # Screenshot all slices
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
        image_file = Image.new('RGB', (slices[0].size[0], actual_page_size))
        for i, img in enumerate(slices[:-1]):
            image_file.paste(img, (0, math.ceil(i * inner_height * device_pixel_ratio)))
        else:
            image_file.paste(slices[-1], (0, math.ceil((scroll_height - inner_height) * device_pixel_ratio)))
        image_file.save(f'{self.SAVE_PATH}/{file_name}', **image_options)

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
