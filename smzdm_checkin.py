#!/usr/bin/env python
#encoding=utf8

from os.path import join, dirname, abspath
import datetime
import selenium
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from config import *


def send_warning_mail():
    return requests.post(
        MAILGUN_API_URL,
        auth=("api", MAILGUN_KEY),
        files=[("inline", open(SCREENSHOT_PATH))],
        data={
            "from": MAILFROM,
            "to": MAILTO,
            "subject": MAIL_TITLE,
            "text": "Testing some Mailgun awesomness!",
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


def has_checkin():
    output_filename = join(dirname(abspath(__file__)), "ret")
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


def checkin():
    output_filename = join(dirname(abspath(__file__)), "ret")
    if not DEBUG and has_checkin():
        return
    browser = webdriver.PhantomJS(service_args=['--load-images=no'])
    browser.set_window_size(1024, 768)
    browser.get("http://www.smzdm.com")

    try:
        element = browser.find_element_by_id("user_info_tosign")
        element.click()

        WebDriverWait(browser, WAITTIME_BEFORE_CLICK).until(
            EC.frame_to_be_available_and_switch_to_it(
                "zhiyou_login_window_iframe"))
        username = browser.find_element_by_id("username")
        password = browser.find_element_by_id("password")
        login_button = browser.find_element_by_id("login_submit")

        username.send_keys(USERNAME)
        password.send_keys(PASSWORD)
        login_button.click()

        WebDriverWait(browser, WAITTIME_AFTER_CLICK).until(
            EC.text_to_be_present_in_element(
                (By.ID, "user_info_tosign"), u"签到"),
            "timeout waiting for checkin button to load")
        checkin_button = browser.find_element_by_id("user_info_tosign")
        checkin_button.click()
        WebDriverWait(browser, WAITTIME_AFTER_CLICK).until(
            EC.text_to_be_present_in_element(
                (By.ID, "user_info_tosign"), u"已签到"),
            "timeout waiting for page to load")
        text_info = browser.find_element_by_id("user_info_tosign").text
        with open(output_filename, "a") as fh:
            fh.write(str(datetime.datetime.now()) + "\t" + text_info.encode(
                "utf8") + "\n")
        browser.save_screenshot(SCREENSHOT_PATH)
    except selenium.common.exceptions.WebDriverException, err:
        page_source_file = join(dirname(abspath(__file__)), "page_source")
        print err
        send_simple_mail(err)
        with open(page_source_file, "w") as fout:
            fout.write(browser.page_source.encode("utf-8"))
    finally:
        browser.quit()


checkin()
