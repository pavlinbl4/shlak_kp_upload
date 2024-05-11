from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def download_folder(path_to_download_folder='/Volumes/big4photo-4/selenium_downloads'):
    preferences = {
        "download.default_directory": path_to_download_folder
    }
    return preferences


def setting_chrome_options():
    preferences = download_folder()
    chrome_options = Options()
    # chrome_options.add_experimental_option("prefs", preferences)
    chrome_options.add_argument("webdriver.chrome.driver=chromedriver")
    # chrome_options.add_argument("--no-sandbox")  # Запуск Chrome без песочницы (sandbox)
    # chrome_options.add_argument("--disable-dev-shm-usage")  # Отключение использования /dev/shm
    # chrome_options.add_argument("--user-data-dir=/path/to/chrome-profile")  # Указание директории профиля
    # chrome_options.add_experimental_option('detach', True)
    # chrome_options.add_argument("--headless")  # фоновый режим
    # chrome_options.add_argument("--ignore-certificate-errors")  # игнорирует ошибки сертификата SSL
    # chrome_options.add_argument("--disable-cache")  # отключает кэширование в браузере
    # chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1280,800")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # невидимость автоматизации
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
    return chrome_options


if __name__ == '__main__':
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=setting_chrome_options())
        driver.get('https://chromedriver.chromium.org/')

    except Exception as e:
        print(e)
