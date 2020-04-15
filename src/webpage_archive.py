import urllib.error
import urllib.parse
import urllib.request

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class WebPageArchive:

    def init(self):
        print("test")

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
        f.close


test = WebPageArchive()
test.read_url()
