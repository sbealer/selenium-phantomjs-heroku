# -*- coding: utf-8 -*-

#from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import time
import os
import json

from flask import Flask, Response, request

from selenium.webdriver import PhantomJS
from selenium.webdriver import DesiredCapabilities
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException

app = Flask(__name__)

@app.route("/")
def default():
    return Response("Nothing to see here.")

@app.route("/sales", methods=['POST'])
def sales():

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36")

    test_url = "http://requestb.in/18h1dbl1"
    login_url = "https://sellercentral.amazon.com/gp/homepage.html"
    report_url = "https://sellercentral.amazon.com/gp/site-metrics/report.html#&reportID=eD0RCS"

    if os.name == 'nt':
        phantomjs_path = "C:\Python27\phantomjs.exe"
        browser = PhantomJS(executable_path=phantomjs_path, desired_capabilities=dcap)
        print("Browser started.")

    else:
        browser = PhantomJS(desired_capabilities=dcap)
        print("Created")

    #browser.set_page_load_timeout(10)
    #browser.implicitly_wait(10)
    wait = ui.WebDriverWait(browser, 20)

    try:

        browser.get(login_url)
        #time.sleep(2)

        wait.until(lambda browser_find: browser.find_element_by_id("signInSubmit"))
        print("Found login page.")
        #wait.until(lambda browser_find: browser.find_element_by_id("ap_email"))
        print("Finding ap_email")
        username = browser.find_element_by_id("ap_email")
        password = browser.find_element_by_id("ap_password")
        print("Found both fields. Gathering credentials.")
        auth1 = os.environ["AZN_AUTH1"]
        auth2 = os.environ["AZN_AUTH2"]
        print("Got Credentials. Attempting to send keys.")
        print(auth1)
        username.send_keys(auth1)
        print("username entered.")
        password.send_keys(auth2)
        time.sleep(1)
        print("password entered.")
        print("Logging in.")
        browser.find_element_by_id("signInSubmit").submit()
        print("Logged in.")
        png = browser.get_screenshot_as_png()
        # return Response(png, mimetype="image/png")
        print("Trying to navigate to report url.")
        browser.get(report_url)
        print("Supposedly navigated...")
        print(browser.title)
        wait.until(lambda browser_find: int(browser.find_element_by_id("summaryOPS")) > 0)
        print("Found summaryOPS element.")
        summary_val = int(browser.find_element_by_id("summaryOPS").text)
        print("Value was: {n}".format(n=summary_val))
        # if summary_val == 0:
        #     print("In loop")
        #     for retry in range(1, 5):
        #         if summary_val != 0:
        #             break
        #         time.sleep(2)
        #         summary_val = int(browser.find_element_by_id("summaryOPS").text)

        if summary_val == 0:
            raise Exception("Could not get sales figures in time or sales were $0")

        resp = {"color": "green","notify": "false","message_format": "text"}
        #
        resp["message"] = summary_val
        print("Trying to return message.")
        return Response(resp)

    except TimeoutException as te:
        # png = browser.get_screenshot_as_png()
        # return Response(png, mimetype="image/png")

        return Response("Couldn't find desired value in specified time limit.")

    except Exception as gen_err:
        #print(gen_err.message)
        return Response(json.dumps({"color": "red",
            "message": "Crap. An error occurred. ",
            "notify": "false",
            "message_format": "text"}))
        # png = browser.get_screenshot_as_png()
        # return Response(png, mimetype="image/png")

    finally:
        browser.quit()

    # png = browser.get_screenshot_as_png()
    # browser.quit()
    #
    # return Response(png, mimetype="image/png")



if __name__ == "__main__":
    app.run(debug=True)


