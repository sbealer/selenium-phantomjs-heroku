# -*- coding: utf-8 -*-
import time
import os
import json
import requests
from flask import Flask, Response
from selenium.webdriver import PhantomJS
from selenium.webdriver import DesiredCapabilities
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException

app = Flask(__name__)

#########################################
debug=True
#########################################

#hipchat_url = 'https://marketfleet.hipchat.com/v2/room/3345643/notification?auth_token=COcvKHKwMGYD509WhwesCqv9KjW5fHGDtDokP4vz'
hipchat_url = 'https://marketfleet.hipchat.com/v2/room/666414/notification?auth_token=tKJOowVhfNg6r9NN560G3EDBnWtpQtj2lboBWIRi'
hipchat_url_dev = 'https://build.hipchat.com/v2/room/2703095/notification?auth_token=6CtGAdfHLnOzfknWh3Os1T74aTc3mIqGusAbVBrL'

good_note = {"color":"green","notify":'false',"message_format":"text"}
bad_note = {'color': 'red', 'notify': 'false', 'message_format': 'text'}

def prnt(text,always_print=False):
    if debug or always_print:
        print(text)

@app.route("/")
def default():
    return Response("Nothing to see here.")

@app.route("/sales", methods=['GET','POST'])
def sales():

    return Response(get_sales())

#######################################################################################################################

#@app.route("/send_notice/<who>", methods=['GET'])
def send_hipchat_note(who):
    print("sending data")
    sales_data = get_sales()
    try:
        if who == 'dev':
            req = requests.post(hipchat_url_dev, data=sales_data, headers={"Content-Type": "application/json"})
            return "Success"
        elif who == 'prd':
            req = requests.post(hipchat_url, data=sales_data, headers={"Content-Type": "application/json"})
            return "Success"

        else:
            return Response("No target.")
    except Exception as e:
        return str(e.message)


#######################################################################################################################

def get_sales():

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36")

    login_url = "https://sellercentral.amazon.com/gp/homepage.html"
    report_url = "https://sellercentral.amazon.com/gp/site-metrics/report.html#&reportID=eD0RCS"

    if os.name == 'nt':
        phantomjs_path = "C:\Python27\phantomjs.exe"
        browser = PhantomJS(executable_path=phantomjs_path, desired_capabilities=dcap)
        prnt("Browser started.", True)

    else:
        browser = PhantomJS(desired_capabilities=dcap)
        prnt("Browser started.", True)

    # browser.set_page_load_timeout(10)
    # browser.implicitly_wait(10)
    wait = ui.WebDriverWait(browser, 20)

    try:

        browser.get(login_url)
        # time.sleep(2)

        wait.until(lambda browser_find: browser.find_element_by_id("signInSubmit"))
        prnt("Found login page.")
        # wait.until(lambda browser_find: browser.find_element_by_id("ap_email"))
        prnt("Finding ap_email")
        username = browser.find_element_by_id("ap_email")
        password = browser.find_element_by_id("ap_password")
        prnt("Found both fields. Gathering credentials.")
        auth1 = os.environ["AZN_AUTH1"]
        auth2 = os.environ["AZN_AUTH2"]
        #prnt("Got Credentials. Attempting to send keys.")
        prnt(auth1)
        username.send_keys(auth1)
        #prnt("username entered.")
        password.send_keys(auth2)
        time.sleep(1)
        #prnt("password entered.")
        prnt("Logging in.")
        browser.find_element_by_id("signInSubmit").submit()
        prnt("Logged in.")
        # png = browser.get_screenshot_as_png()
        # return Response(png, mimetype="image/png")
        prnt("Trying to navigate to report url.")
        browser.get(report_url)
        prnt("Supposedly navigated...")
        prnt(browser.title)
        wait.until(lambda browser_find: browser.find_element_by_id("summaryOPS"))
        prnt("Found summaryOPS element.")
        summary_val = browser.find_element_by_id("summaryOPS").text
        prnt("Value was: {n}".format(n=summary_val))
        if summary_val == '0':
            prnt("In loop")
            for retry in range(1, 5):
                if summary_val != '0':
                    break
                time.sleep(2)
                summary_val = browser.find_element_by_id("summaryOPS").text

        if summary_val == 0:
            raise Exception("Could not get sales figures in time or sales were $0")

        resp = good_note

        resp["message"] = "Marketfleet hourly sales notification: " + summary_val
        prnt("Trying to return message.")
        return json.dumps(resp)

    except TimeoutException as te:
        prnt("Couldn't find desired value in specified time limit.")
        return "Couldn't find desired value in specified time limit."

    except Exception as gen_err:
        prnt(gen_err.message)
        error_text = bad_note
        error_text["message"] = "An error occurred: {e}".format(e=gen_err.message)
        prnt(json.dumps(error_text))
        return json.dumps(error_text)

        # png = browser.get_screenshot_as_png()
        # return Response(png, mimetype="image/png")

    finally:
        browser.quit()

        # png = browser.get_screenshot_as_png()
        # browser.quit()
        #
        # return Response(png, mimetype="image/png")

#######################################################################################################################

if __name__ == "__main__":
    app.run(debug=False)


