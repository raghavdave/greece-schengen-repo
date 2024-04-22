# uses selenium to scrape website
# you 'll need to download webdriver for Google Chrome to run this application
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from urllib import request as req
import datetime
import json


def main_func():
    url = "https://appointment.mfa.gr/en/reservations/aero/ireland-grcon-dub/"
    total_slots = 0
    error = 0
    try:
        driver = webdriver.Chrome()
        driver.get(url)
        landing_page = driver.find_elements(By.CLASS_NAME, "aero_abtnbook")
        landing_page[0].click()
        time.sleep(1)
        num_months = 5
        while num_months:
            available_slots = 0
            month_val = driver.find_elements(By.CLASS_NAME, "aero_cal_navcur")[
                0
            ].text
            time.sleep(1)
            print("Starting New Month:", month_val)
            available_dates = driver.find_elements(
                By.CLASS_NAME, "aero_bcal_tdopen"
            )
            print("Available Dates:", len(available_dates))
            for i in available_dates:
                i.click()
                available_times = driver.find_elements(
                    By.CLASS_NAME, "aero_bcal_ptime"
                )
                available_slots += len(available_times)
            print("Available Timeslots:", available_slots)
            total_slots += available_slots
            num_months -= 1
            next_month = driver.find_elements(By.CLASS_NAME, "aero_cal_nav")
            next_month[-1].click()
            time.sleep(1)
        print("----Total Slots Found:", total_slots)
        driver.close()
    except Exception as e:
        print(str(e))
        error += 1
    return total_slots, error


def send_notification(hook, num_slots):
    request = req.Request(url=hook, method="POST")
    request.add_header(key="Content-Type", val="html")
    notification_time = datetime.datetime.utcnow().strftime(
        "%m-%d-%Y %H:%M UTC"
    )
    data = json.dumps(
        {
            "title": f"Greece Appointment Slots Available at {notification_time}!",
            "text": f"{num_slots} Slots Available",
            "themeColor": "E81123",
        }
    ).encode()
    with req.urlopen(url=request, data=data) as response:
        if response.status != 200:
            print("Unable to send Teams Notification")


# put microsoft teams webhook below, and uncomment line
teams_webhook = ()

# searches 20 times, every 15 minutes
num_tries = 20

while num_tries:
    slots, err = main_func()
    if slots > 0:
        print("Slots Found")
    # if you have teams webhook, uncomment the below line
    # send_notification(teams_webhook, slots)
    num_tries -= 1
    # searches for slot every 15 minutes
    time.sleep(900)
