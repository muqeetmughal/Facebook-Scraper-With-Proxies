import re
import time
import urllib.parse
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from utils import get_random_proxy
from webdriver_manager.chrome import ChromeDriverManager
import seleniumwire.undetected_chromedriver as uc

class WebScraper:
    def __init__(self, proxy_list, input_csv, output_csv):
        self.proxy_list = proxy_list
        self.input_csv = input_csv
        self.output_csv = output_csv

        self.proxy_url = get_random_proxy(self.proxy_list)
        print("Using proxy:", self.proxy_url)

        # Configure Selenium options
        self.seleniumwire_options = {
            "proxy": {"http": self.proxy_url, "https": self.proxy_url},
        }
        self.chrome_options = Options()
        self.chrome_options.add_argument("--disable-gpu")

        # self.driver = webdriver.Chrome(
        #     service=ChromeService(ChromeDriverManager().install()),
        #     options=self.chrome_options,
        #     seleniumwire_options=self.seleniumwire_options,
        # )
        self.driver = uc.Chrome(options=self.chrome_options, seleniumwire_options=self.seleniumwire_options)


    def extract_page_name(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            h1_element = self.driver.find_element(By.TAG_NAME, "h1")
            return h1_element.text.strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""

    def extract_phone_numbers(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            page_content = self.driver.page_source
            phone_pattern = re.compile(
                r"(\+48\s\d{3}\s\d{3}\s\d{3})|(\+\d{1,3}\s\d{1,4}\s\d{3}\s\d{2}\s\d{2})"
            )
            phone_numbers = phone_pattern.findall(page_content)
            phone_numbers = [number for group in phone_numbers for number in group if number]
            return list(set(phone_numbers))
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def extract_emails(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            page_content = self.driver.page_source
            email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
            return list(set(email_pattern.findall(page_content)))
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def get_all_urls(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            anchors = self.driver.find_elements(By.TAG_NAME, "a")
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

    def process_urls(self):
        with open(self.input_csv, newline="", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            next(reader)
            with open(self.output_csv, mode="w", newline="", encoding="utf-8") as outfile:
                writer = csv.writer(outfile)
                writer.writerow([
                    "URL", "Page Name", "Phone Numbers", "Emails", "Website URLs"
                ])
                for row in reader:
                    url = row[0]
                    print(f"Processing URL: {url}")
                    self.driver.get(url)
                    page_name = self.extract_page_name()
                    phone_numbers = self.extract_phone_numbers()
                    emails = self.extract_emails()
                    urls = self.get_all_urls()

                    writer.writerow([
                        url,
                        page_name,
                        "; ".join(phone_numbers),
                        "; ".join(emails),
                        "; ".join(urls[:1]),
                    ])

                    for extra_url in urls[1:]:
                        writer.writerow(["", "", "", "", extra_url])

                    time.sleep(2)

    def quit(self):
        self.driver.quit()

if __name__ == "__main__":
    proxy_list = [
        "195.216.158.166:29842:kjasis:axQ6cnwT",
        "195.216.158.94:29842:kjasis:axQ6cnwT",
    ]
    input_csv = "input.csv"
    output_csv = "output_sample.csv"

    scraper = WebScraper(proxy_list, input_csv, output_csv)
    scraper.process_urls()
    scraper.quit()
