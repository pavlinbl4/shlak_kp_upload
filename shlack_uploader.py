from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from kp_selenium_tools.authorization import AuthorizationHandler
from photo_id import extract_photo_id


def find_element(driver, selector):
    return WebDriverWait(driver, 5).until(EC.element_to_be_clickable(selector))


def upload_file(driver, path_to_file, upload_button_selector):
    upload_button = find_element(driver, upload_button_selector)
    upload_button.send_keys(path_to_file)


def fill_field(driver, field_selector, text):
    field = find_element(driver, field_selector)
    field.clear()
    field.send_keys(text)


def main(path_to_file, image_caption, author):
    driver = AuthorizationHandler().authorize()
    driver.get('https://image.kommersant.ru/photo/archive/adm/AddPhoto.aspx?shootid=429379')

    upload_file(driver, path_to_file, (By.XPATH, "//input[@id='InputFile']"))
    find_element(driver, (By.XPATH, "//input[@type='submit']")).click()

    description_field_selector = (By.XPATH, '//textarea[@name="DescriptionControl$Description"]')
    fill_field(driver, description_field_selector, image_caption)

    author_field_selector = (By.XPATH, '//input[@name="DescriptionControl$NewPseudonym"]')
    fill_field(driver, author_field_selector, author)

    add_photo_button_selector = (By.XPATH, '//input[@name="AddPhotoButton"]')
    find_element(driver, add_photo_button_selector).click()

    wait_for_load = (By.XPATH, "//span[@id='RecentyAddedHeader']")
    find_element(driver, wait_for_load)

    current_url = driver.current_url
    return extract_photo_id(current_url)


if __name__ == '__main__':
    main('/Volumes/big4photo/Downloads/0043_weddtime.ru_7_11zon.jpg',
         'Круглый стол «Коммерческая недвижимость. Акценты-2024»',
         'Антон Волошин')
