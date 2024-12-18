import re
import time
import urllib.parse
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from utils import get_random_proxy


proxy_list = [
        "195.216.158.166:29842:kjasis:axQ6cnwT",
        "195.216.158.94:29842:kjasis:axQ6cnwT",
    ]
proxy_url = get_random_proxy(proxy_list)
print("Using proxy: ",proxy_url)
# set selenium-wire options to use the proxy
seleniumwire_options = {
    "proxy": {"http": proxy_url, "https": proxy_url},
}

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    options=chrome_options,
    seleniumwire_options=seleniumwire_options,
)


def extract_page_name():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        h1_element = driver.find_element(By.TAG_NAME, "h1")
        page_name = h1_element.text.strip()
        return page_name
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def extract_phone_numbers():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        page_content = driver.page_source

        phone_pattern = re.compile(
            r"(\+48\s\d{3}\s\d{3}\s\d{3})|(\+\d{1,3}\s\d{1,4}\s\d{3}\s\d{2}\s\d{2})"
        )
        phone_numbers = phone_pattern.findall(page_content)

        phone_numbers = [
            number for group in phone_numbers for number in group if number
        ]

        unique_phone_numbers = list(set(phone_numbers))

        return unique_phone_numbers

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def extract_emails():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        page_content = driver.page_source
        email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        emails = email_pattern.findall(page_content)
        unique_emails = list(set(emails))
        return unique_emails
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def get_all_urls():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        anchors = driver.find_elements(By.TAG_NAME, "a")
        urls = [
            anchor.get_attribute("href")
            for anchor in anchors
            if anchor.get_attribute("href") is not None
        ]
        filtered_urls = [
            url
            for url in urls
            if re.match(r"^https://l\.facebook\.com/l\.php\?u=.*", url)
        ]

        cleaned_urls = []
        for url in filtered_urls:
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            if "u" in query_params:
                original_url = query_params["u"][0]
                cleaned_url = urllib.parse.unquote(original_url)
                if cleaned_url.startswith("http"):
                    cleaned_urls.append(cleaned_url)

        return cleaned_urls

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def process_urls(input_csv, output_csv):

    with open(input_csv, newline="", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        next(reader)
        with open(output_csv, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)

            writer.writerow(
                ["URL", "Page Name", "Phone Numbers", "Emails", "Website URLs"]
            )

            for row in reader:
                url = row[0]
                print(f"Processing URL: {url}")
                driver.get(url)
                page_name = extract_page_name()
                phone_numbers = extract_phone_numbers()
                emails = extract_emails()
                urls = get_all_urls()

                data_to_write = [
                    url,
                    page_name,
                    "; ".join(phone_numbers),
                    "; ".join(emails),
                    "; ".join(urls[:1]),
                ]

                writer.writerow(
                    data_to_write
                )  # Write first URL in the "Extracted URLs" column

                for extra_url in urls[1:]:
                    writer.writerow(["", "", "", "", extra_url])

                time.sleep(2)


input_csv = "input.csv"
output_csv = "output_sample.csv"

process_urls(input_csv, output_csv)

driver.quit()
