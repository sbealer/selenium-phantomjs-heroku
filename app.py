# -*- coding: utf-8 -*-

#from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import time
import os

from flask import Flask, Response, request

from selenium.webdriver import PhantomJS
from selenium.webdriver import DesiredCapabilities
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException

app = Flask(__name__)


# class StderrLog(object):
#     def close(self):
#         pass
#
#     def __getattr__(self, name):
#         return getattr(sys.stderr, name)
#
#
# class Driver(PhantomJS):
#     def __init__(self, *args, **kwargs):
#         super(Driver, self).__init__(*args, **kwargs)
#         self._log = StderrLog()

# @app.route("/old")
# def index():
#     url = request.args.get("url", "")
#     width = int(request.args.get("w", 1000))
#     min_height = int(request.args.get("h", 400))
#     wait_time = float(request.args.get("t", 20)) / 1000  # ms
#
#     if not url:
#         return "Example: <a href='http://selenium-phantomjs-test.herokuapp.com/?url=http://en.ig.ma/&w=1200'>" \
#                "http://selenium-phantomjs-test.herokuapp.com/?url=http://en.ig.ma/</a>"
#
#     driver = Driver()
#     driver.set_window_position(0, 0)
#     driver.set_window_size(width, min_height)
#
#     driver.set_page_load_timeout(20)
#     driver.implicitly_wait(20)
#     driver.get(url)
#
#     driver.set_window_size(width, min_height)
#     time.sleep(wait_time)
#
#     sys.stderr.write(driver.execute_script("return document.readyState") + "\n")
#
#     png = driver.get_screenshot_as_png()
#     driver.quit()
#
#     return Response(png, mimetype="image/png")


@app.route("/")
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
        # browser.get(test_url)
        # exit()


        browser.get(login_url)
        time.sleep(2)

        print(browser.title)

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
        #time.wait(1)
        password.send_keys(auth2)
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
        wait.until(lambda browser_find: browser.find_element_by_id("summaryOPS"))

        summary_val = browser.find_element_by_id("summaryOPS").text

        return Response(summary_val)

    except TimeoutException as te:
        png = browser.get_screenshot_as_png()
        return Response(png, mimetype="image/png")
        #return Response("Couldn't find desired value in specified time limit.")

    except Exception as gen_err:
        return Response("Error occurred! <br/> " + browser.page_source)
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


