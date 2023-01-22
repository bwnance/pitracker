import os
import requests
import re
from IPython import embed
from dotenv import load_dotenv
import time
from smtp_server import SMTPServer
import selenium_handler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
import css_inline

DENYLISTED_URLS = [
    "https://www.digikey.com/en/products/detail/raspberry-pi/SC0694/13530925",
]
load_dotenv()
jinja_env = Environment(
    loader=FileSystemLoader("email_templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

countries = os.getenv("COUNTRIES").split(",")
countries_regex = "|".join(countries)
sku_prefixes = os.getenv("SKU_PREFIXES").split(",")
sku_prefixes_regex = "|".join(sku_prefixes)

email_recipients = os.getenv("EMAILS").split(",")
sender_email = os.getenv("SENDER_EMAIL")


def get_pi_data():

    (
        cfid,
        cftoken,
        local_token,
        other_token,
    ) = selenium_handler.get_cf_info_and_localtoken()

    cur_epoch = str(int(time.time() * 1000))
    url = "https://rpilocator.com/data.cfm"

    query_params = {
        "method": "getProductTable",
        "token": other_token,
        # "country": country,
        "_": cur_epoch,
    }
    headers = {
        "cookie": f"cfid={cfid}; cftoken={cftoken}; RPILOCATOR=0; CFID={cfid}; CFTOKEN={cftoken}",
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://rpilocator.com/",
        "accept": "application/json, text/javascript, */*; q=0.01",
    }

    response = requests.get(url, headers=headers, params=query_params)
    return response.json()["data"]


def parse_pi_data(pi_data):
    instock = [datum for datum in pi_data if datum["avail"] != "No"]
    matching_pis = []
    for instock_pi in instock:
        if instock_pi["link"] in DENYLISTED_URLS:
            continue
        if re.search(sku_prefixes_regex, instock_pi["sku"]) and re.search(
            countries_regex, instock_pi["vendor"]
        ):
            matching_pis.append(instock_pi)

    return matching_pis


def notify(instock_pis):
    email_server = SMTPServer()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "In-stock Raspberry Pis"
    msg["From"] = sender_email
    msg["To"] = ",".join(email_recipients)
    template = jinja_env.get_template("email_template.html")
    html = template.render(pi_data=instock_pis)
    inlined_html = css_inline.inline(html)
    part = MIMEText(inlined_html, "html")
    msg.attach(part)
    email_server.send_email(email_recipients, msg.as_string())
    # with open("email.html", "w") as f:
    #     f.write(inlined_html)


def run():
    pi_data = get_pi_data()
    instock_pis = parse_pi_data(pi_data)
    if len(instock_pis) > 0:
        notify(instock_pis)
    else:
        print("no pis, sorry!")


if __name__ == "__main__":
    run()
