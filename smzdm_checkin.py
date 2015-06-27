#!/usr/bin/env python
#encoding=utf8

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from config import *

browser = webdriver.PhantomJS(service_args=['--load-images=no'])
browser.set_window_size(1024, 768)
browser.get("http://www.smzdm.com")

element = browser.find_element_by_id("navBar_login")
element.click()

username = browser.find_element_by_id("user_login")
password = browser.find_element_by_id("user_pass")
login_button = browser.find_element_by_id("btn_login")

username.send_keys(USERNAME)
password.send_keys(PASSWORD)
login_button.click()

WebDriverWait(browser, 10).until(
            lambda x: len(x.find_element_by_id("user_info_score").text) > 0
        )
checkin_button = browser.find_element_by_id("user_info_tosign")
checkin_button.click()
browser.save_screenshot(SCREENSHOT_PATH)

browser.quit()
