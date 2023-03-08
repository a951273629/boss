from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import subprocess
import time


class Browser:
    def __init__(self):
        self.browser = self.init_webdriver()
        pass

    def init_webdriver(self):
        # subprocess.call(r'runas /user:SYSTEM .\start.bat')

        chrome_options = Options()
        chrome_options.add_experimental_option(
            'debuggerAddress', '127.0.0.1:9228')
        browser = webdriver.Chrome(options=chrome_options)
        browser.execute_script(
            'window.open("https://www.zhipin.com/web/geek/job?query=&page=4")')
        return browser

    def fresh_cookie(self):
        self.browser.refresh()
        # 等待所有请求加载完成
        self.browser.implicitly_wait(30)
        time.sleep(1.5)
        cookies = {}
        for cookie in self.browser.get_cookies():
            cookies[cookie['name']] = cookie['value']
        return cookies


# b = Browser()
# b.fresh_cookie()
