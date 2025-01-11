"""
this function upload image to archive via web uploader
"""

import os

from loguru import logger
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from kp_selenium_tools.authorization import AuthorizationHandler
from photo_uplolader.photo_id import extract_photo_id

logger.add("../photo_uploader.log", format="{time} {level} {message}", level="INFO")


def find_element(driver, selector):
    return WebDriverWait(driver, 5).until(EC.element_to_be_clickable(selector))


def upload_file(driver, path_to_file, upload_button_selector):
    upload_button = find_element(driver, upload_button_selector)
    upload_button.send_keys(path_to_file)


def fill_field(driver, field_selector, text):
    field = find_element(driver, field_selector)
    field.clear()
    field.send_keys(text)


def web_photo_uploader(path_to_file, image_caption, author, internal_shoot_id='434484'):
    try:
        driver = AuthorizationHandler().authorize()
        if driver.title == 'Фотоархив ИД "Коммерсантъ" | Поиск':
            logger.info("Authorization successful")
        upload_link = f'https://image.kommersant.ru/photo/archive/adm/AddPhoto.aspx?shootid={internal_shoot_id}'
        driver.get(upload_link)
        # logger.info(driver.title)
        logger.info(find_element(driver, (By.XPATH, '//*[@id="HeaderText"]')).text)
    except TimeoutException as e:
        logger.error(f"Timeout occurred: {e}")
    except Exception as ex:
        logger.error(f"An error occurred: {ex}")






    upload_file(driver, path_to_file, (By.XPATH, "//input[@id='InputFile']"))
    find_element(driver, (By.XPATH, "//input[@type='submit']")).click()

    description_field_selector = (By.XPATH, '//textarea[@name="DescriptionControl$Description"]')
    fill_field(driver, description_field_selector, image_caption)

    author_field_selector = (By.XPATH, '//input[@name="DescriptionControl$NewPseudonym"]')
    fill_field(driver, author_field_selector, author)

    # find upload photo button and click it
    add_photo_button_selector = (By.XPATH, '//input[@name="AddPhotoButton"]')
    find_element(driver, add_photo_button_selector).click()

    wait_for_load = (By.XPATH, "//span[@id='RecentyAddedHeader']")
    find_element(driver, wait_for_load)

    current_url = driver.current_url
    logger.info(current_url)

    # remove file after upload
    os.remove(path_to_file)
    photo_id = extract_photo_id(current_url)
    logger.info(photo_id)
    return photo_id


if __name__ == '__main__':
    web_photo_uploader('/Users/evgeniy/Downloads/IMG_9466.JPG',
                       'Фармацевтический завод «Фарма Капитал»',
                       'АО «Российский аукционный дом»',
                       internal_shoot_id='434484')
