#!/usr/bin/env python
#encoding=utf8

from os.path import join, dirname, abspath
import datetime
import selenium
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException
import requests
from config import *


def ajax_complete(driver):
    try:
        return 0 == driver.execute_script("return jQuery.active")
    except WebDriverException:
        pass

def send_warning_mail():
    return requests.post(
        MAILGUN_API_URL,
        auth=("api", MAILGUN_KEY),
        files=[("inline", open(SCREENSHOT_PATH))],
        data={"from": MAILFROM,
              "to": MAILTO,
              "subject": MAIL_TITLE,
              "text": "Testing some Mailgun awesomness!",
              "html": '<html>Inline image here: <img src="cid:smzdm.png"></html>'})

def checkin():
    output_filename = join(dirname(abspath(__file__)), "ret")
    with open(output_filename, "r") as fh:
        lines = fh.readlines()
        line = lines[-1]
        date, _, result = line.split()
        if date == datetime.datetime.strftime(
            datetime.datetime.now().date(), "%Y-%m-%d"):
            if result.find("已签到") != -1:
                return
            else:
                send_warning_mail()
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

    WebDriverWait(browser, WAITTIME_BEFORE_CLICK).until(
        lambda x: len(x.find_element_by_id("user_info_score").text) > 0)
    WebDriverWait(browser, WAITTIME_BEFORE_CLICK).until(
        ajax_complete, "timeout waiting for page to load")
    checkin_button = browser.find_element_by_id("user_info_tosign")
    checkin_button.click()
    WebDriverWait(browser, WAITTIME_AFTER_CLICK).until(
        ajax_complete, "timeout waiting for page to load")
    text_info = browser.find_element_by_id("user_info_tosign").text
    with open(output_filename, "a") as fh:
        fh.write(str(datetime.datetime.now()) + "\t" + text_info.encode("utf8")
                 + "\n")
    browser.save_screenshot(SCREENSHOT_PATH)

    browser.quit()


checkin()
