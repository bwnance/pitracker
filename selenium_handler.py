import os
import re
from threading import local
from seleniumwire import webdriver
from urllib.parse import parse_qs, urlparse
from selenium.webdriver.chrome.options import Options


DRIVER_FOLDER = "./drivers/"


def init_selenium():
    driver_path = os.getenv("CHROME_DRIVER_PATH")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(
        executable_path=driver_path, options=chrome_options
    )
    return driver


def get_cf_info_and_localtoken():
    driver = init_selenium()
    driver.get("https://rpilocator.com")
    data_request = [
        request
        for request in driver.requests
        if "rpilocator.com/data.cfm" in request.url
    ][0]
    cookie_header = data_request.headers.get("cookie")

    cfid = re.match(r"cfid=(.{8}-.{4}-.{4}-.{4}-.{12});", cookie_header).group(
        1
    )
    local_token = parse_qs(urlparse(data_request.url).query)["token"][0]
    cftoken = "0"
    driver.quit()
    return cfid, cftoken, local_token
