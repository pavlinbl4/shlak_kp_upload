# pip install webdriver-manager

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from get_credentials import Credentials
from kp_selenium_tools.crome_options import setting_chrome_options


class AuthorizationHandler:
    def __init__(self):
        self.service = Service(ChromeDriverManager().install())
        self.driver = None

    def setup_driver(self):
        self.driver = webdriver.Chrome(service=self.service, options=setting_chrome_options())

    def perform_authorization(self):
        login = Credentials().kp_login
        password = Credentials().kp_password
        first_login = Credentials().first_login
        self.driver.get(first_login)
        login_input = self.driver.find_element("id", "login")
        login_input.send_keys(login)
        password_input = self.driver.find_element("id", "password")
        password_input.send_keys(password)
        self.driver.find_element("name", "loginbtn").click()

    def get_driver(self):
        return self.driver

    def authorize(self):
        self.setup_driver()
        self.perform_authorization()
        return self.get_driver()


if __name__ == '__main__':
    authorization_handler = AuthorizationHandler()
    authorization_handler.authorize()
"""

This code defines a class `AuthorizationHandler` that encapsulates the logic for handling authorization. 
The `setup_driver` method initializes the WebDriver, `perform_authorization` handles the actual authorization process,
and `get_driver` returns the WebDriver instance. The `authorize` method combines these steps for easy authorization.
"""
