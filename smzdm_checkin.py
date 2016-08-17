#!/usr/bin/env python
#encoding=utf8

from os.path import join, dirname, abspath, isfile
import datetime
import time
import selenium
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import traceback
import requests
from config import *

login_button_tag = "J_login_trigger"
login_iframe_tag = "J_login_iframe"
checkin_button_tag = "J_punch"
login_score_tag = "user_info_tosign"

def send_warning_mail(content):
    if not DEBUG:
        return requests.post(
            MAILGUN_API_URL,
            auth=("api", MAILGUN_KEY),
            files=[("inline", open(SCREENSHOT_PATH))],
            data={
                "from": MAILFROM,
                "to": MAILTO,
                "subject": MAIL_TITLE,
                "text": content,
                "html": '<html>Inline image here: <img src="cid:smzdm.png"></html>'
            })

def send_simple_mail(content):
    return requests.post(
        MAILGUN_API_URL,
        auth=("api", MAILGUN_KEY),
        data={
            "from": MAILFROM,
            "to": MAILTO,
            "subject": MAIL_TITLE,
            "text": content,
        }, )


def loop_try(browser):
    checkin_button = browser.find_element_by_class_name(checkin_button_tag)
    count = 0
    while True:
        try:
            text_info = browser.find_element_by_class_name(checkin_button_tag).text
        except:
            text_info = browser.find_element_by_id(login_score_tag)
        if text_info.find(u"已签到") == 0 or text_info.find(u"已经签到") == 0:
            break
        else:
            print("not found")
            checkin_button.click()
            time.sleep(3)
            count = count + 1
            if count == TIMEOUT_TRY_COUNT:
                raise selenium.common.exceptions.WebDriverException("try to click checkin so many times!")

def has_checkin():
    output_filename = join(dirname(abspath(__file__)), "ret")
    if not isfile(output_filename): return False
    with open(output_filename, "r") as fh:
        lines = fh.readlines()
        line = lines[-1]
        date, _, result = line.split()
        if date == datetime.datetime.strftime(
            datetime.datetime.now().date(), "%Y-%m-%d"):
            if result.find("已签到") != -1:
                return True
            else:
                send_warning_mail()
                return False
        else:
            return False

def login(browser):
    WebDriverWait(browser, WAITTIME_BEFORE_CLICK).until(
        EC.frame_to_be_available_and_switch_to_it(
            login_iframe_tag))
    username = browser.find_element_by_id("username")
    password = browser.find_element_by_id("password")
    login_button = browser.find_element_by_id("login_submit")

    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)
    login_button.click()
    print("click login")
    WebDriverWait(browser, WAITTIME_BEFORE_CLICK).until(
        EC.invisibility_of_element_located((By.ID, "login_submit")),
        "timeout waiting for login window disappear")

def checkin():
    output_filename = join(dirname(abspath(__file__)), "ret")
    if not DEBUG and has_checkin():
        return
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = USER_AGENT
    browser = webdriver.PhantomJS(service_args=['--load-images=no'], desired_capabilities=dcap)
    browser.set_window_size(1024, 768)
    browser.get("http://www.smzdm.com/")

    try:
        WebDriverWait(browser, WAITTIME_BEFORE_CLICK).until(
            EC.element_to_be_clickable((By.CLASS_NAME, login_button_tag)),
            "timeout waiting for login button to load")
        element = browser.find_element_by_class_name(login_button_tag)
        element.click()

        login(browser)

        WebDriverWait(browser, WAITTIME_BEFORE_CLICK).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, checkin_button_tag), u"签到"),
            "timeout waiting for checkin button to load")
        checkin_button = browser.find_element_by_class_name(checkin_button_tag)

        WebDriverWait(browser, WAITTIME_BEFORE_CLICK).until(
            EC.element_to_be_clickable((By.CLASS_NAME, checkin_button_tag)),
            "timeout waiting for checkin button to be clickable")
        WebDriverWait(browser, WAITTIME_AFTER_CLICK).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, checkin_button_tag), u"签到"),
            "timeout waiting for page to load")
        checkin_button = browser.find_element_by_class_name(checkin_button_tag)
        checkin_button.click()
        print("click checkin")
        loop_try(browser)
        text_info = browser.find_element_by_class_name(checkin_button_tag).text
        with open(output_filename, "a") as fh:
            fh.write(str(datetime.datetime.now()) + "\t" + text_info.encode(
                "utf8") + "\n")
        print text_info.encode("utf8")
        browser.save_screenshot(SCREENSHOT_PATH)
    except selenium.common.exceptions.WebDriverException, err:
        page_source_file = join(dirname(abspath(__file__)), "page_source")
        tb = traceback.format_exc()
        print err
        print tb
        browser.save_screenshot(SCREENSHOT_PATH)
        send_warning_mail(str(err) + "\n" + tb)
        with open(page_source_file, "w") as fout:
            fout.write(browser.page_source.encode("utf-8"))
    finally:
        browser.quit()


checkin()
