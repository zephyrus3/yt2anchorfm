from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import logging
import time

ANCHOR_URL = 'https://anchor.fm/'
logger = logging.getLogger("ANCHOR_SELENIUM")


class AnchorFmHelper:
    def __init__(self, driver, email, password):
        self.driver = driver
        self.email = email
        self.password = password

    def loggin_anchor(self):
        URL = ANCHOR_URL + "login"
        logger.info(f"Loading page: {URL}")
        self.driver.get(URL)

        logger.info("Waiting for page elements to be ready")
        email_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'email')))

        password_element = self.driver.find_element(By.ID, "password")

        logger.info("Inserting email")
        email_element.send_keys(self.email)

        logger.info("Inserting password")
        password_element.send_keys(self.password)

        password_element.send_keys(Keys.RETURN)
        WebDriverWait(self.driver, 10).until(EC.title_contains("Dashboard"))

    def upload_audio(self, audio_path):
        URL = ANCHOR_URL + "dashboard/episode/new"

        logger.info(f"Loading Upload page: {URL}")
        self.driver.get(URL)
        WebDriverWait(self.driver, 10).until(EC.title_contains("episode"))

        logger.info("Waiting for Upload file button to be available")
        inputFile = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@type='file']")))

        logger.info("Uploading audio file")
        self.driver.execute_script("arguments[0].style.display = 'block';",
                                   inputFile)
        inputFile.send_keys(audio_path)

        logger.info("Waiting for Save button to be available")
        saveButton = WebDriverWait(self.driver, 200).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".styles__saveButton___lWrNZ")))

        saveButton.click()

    def fill_episode_data(self, title, desc):
        logger.info('Waiting for title and description fields to be ready')

        time.sleep(3)

        titleField = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.ID, "title")))
        logger.info(f'Adding title: "{title}"')
        self.sendKeysWithEmojis(titleField, title)

        descField = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div[role="textbox"]')))
        # // Wait some time so any field refresh doesn't mess up with our input

        logger.info(f'Adding description: "{desc}"')
        descField.send_keys(desc)

        logger.info("Publishing")
        found_end_btn = False

        for button_label in ("Publish now", "Next"):
            if not found_end_btn:
                logger.info(
                    f'Looking for a button with label: "{button_label}"')
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH,
                             f'//button[normalize-space()="{button_label}"]'
                             ))).click()
                except:
                    logger.info(
                        f'Failed to found button with label: "{button_label}"')
                else:
                    logger.info(f'Found button...')
                    found_end_btn = True

        if not found_end_btn:
            logger.warn(
                "Failed to publish episode title/description. Aborting")
            raise Exception("Failed to publish episode")

        WebDriverWait(self.driver, 60).until_not(
            EC.presence_of_element_located((By.ID, "title")))
