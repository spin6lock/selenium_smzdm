#!/usr/bin/env python
#encoding=utf8

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from config import *

browser = webdriver.Firefox()
browser.get("http://smzdm.com")

element = browser.find_element_by_id("navBar_login")
element.click()

username = browser.find_element_by_id("user_login")
password = browser.find_element_by_id("user_pass")
login_button = browser.find_element_by_id("btn_login")

username.send_keys(USERNAME)
password.send_keys(PASSWORD)
login_button.click()

WebDriverWait(browser, 10).until(
                lambda x: x.find_element_by_id('user_info_tosign').is_displayed())
checkin_button = browser.find_element_by_id("user_info_tosign")
checkin_button.click()
