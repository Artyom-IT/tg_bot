import time
import csv
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

SCROLL_PAUSE_TIME = 1.5
SCROLL_HEIGHT = 200
SCROLL_TIMES = 10
URL = "https://coinmarketcap.com/?page={}"
driver = webdriver.Chrome(ChromeDriverManager().install())


def delete_file(file_name):
    os.remove(f"./../data/{file_name}")


def write_csv(data):
    with open(f"./../data/crypto.csv", "a") as file:
        writer = csv.writer(file)
        writer.writerow([data["full_name"], data["short_name"], data["price"]])


def setup_webdriver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')


def load_content(driver, scroll_height, scroll_times, scroll_pause_time):
    while True:

        driver.execute_script(f"window.scrollTo({scroll_height},{scroll_height + 1500});")
        time.sleep(scroll_pause_time)
        scroll_times -= 1
        scroll_height += 700

        if scroll_times == 0:
            break


def parse(url, scroll_height, scroll_times, scroll_pause_time):
    res = []
    setup_webdriver()

    driver.get(url)

    load_content(driver, scroll_height, scroll_times, scroll_pause_time)

    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    my_data = soup.find("table", class_="cmc-table").find("tbody").find_all("tr")

    for data in my_data:
        tds = data.find_all('td')
        try:
            full_name = tds[2].find("p", class_="iJjGCS").text
            short_name = tds[2].find("p", class_="coin-item-symbol").text
            price = tds[3].find("a", class_="cmc-link").text

            result = {
                'full_name': full_name,
                'short_name': short_name,
                'price': price
            }
            res.append(result)
            write_csv(result)
        except (IndexError, AttributeError):
            print("Some error occurred!")

    return res


def main():
    try:
        delete_file("crypto.csv")
    except FileNotFoundError:
        print("ooppps")
    for page in range(1, 10):
        url = URL.format(page)
        parse(url, SCROLL_HEIGHT, SCROLL_TIMES, SCROLL_PAUSE_TIME)

    driver.quit()


if __name__ == "__main__":
    main()
