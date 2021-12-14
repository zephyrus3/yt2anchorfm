from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as SeleniumExceptions

import logging
import time

ANCHOR_URL = 'https://anchor.fm/'
logger = logging.getLogger("ANCHOR_SELENIUM")

DEFAULT_TIMEOUT = 60


class AnchorFmHelper:
    def __init__(self, driver, email, password):
        self.driver = driver
        self.email = email
        self.password = password

    def logging_anchor(self):
        URL = ANCHOR_URL + "login"
        logger.info(f"Loading page: {URL}")
        self.driver.get(URL)

        logger.info("Waiting for page elements to be ready")
        email_element = WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, 'email')))

        password_element = self.driver.find_element(By.ID, "password")

        logger.info("Inserting email")
        email_element.send_keys(self.email)

        logger.info("Inserting password")
        password_element.send_keys(self.password)

        password_element.send_keys(Keys.RETURN)
        WebDriverWait(self.driver,
                      DEFAULT_TIMEOUT).until(EC.title_contains("Dashboard"))

    def upload_audio(self, audio_path):
        URL = ANCHOR_URL + "dashboard/episode/new"

        logger.info(f"Loading Upload page: {URL}")
        self.driver.get(URL)
        WebDriverWait(self.driver,
                      DEFAULT_TIMEOUT).until(EC.title_contains("episode"))

        logger.info("Waiting for Upload file button to be available")
        inputFile = WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
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

    def publish_episode(self, title, desc):
        logger.info('Waiting for title and description fields to be ready')

        time.sleep(3)

        titleField = WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "title")))
        logger.info(f'Adding title: "{title}"')
        titleField.send_keys(title)

        descField = WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
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
                    WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
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

        WebDriverWait(self.driver, DEFAULT_TIMEOUT).until_not(
            EC.presence_of_element_located((By.ID, "title")))

    def remove_episodes(self, keep_episodes_num):
        URL = ANCHOR_URL + "dashboard/episodes"

        logger.info(f"Loading Episodes page: {URL}")
        self.driver.get(URL)

        keep_removing = True

        while keep_removing:
            EPISODE_LIST_CSS_SELECTOR = ".css-axjbiw"

            try:
                episodes_list = WebDriverWait(
                    self.driver, DEFAULT_TIMEOUT).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, EPISODE_LIST_CSS_SELECTOR)))

                items = episodes_list.find_elements(By.TAG_NAME, "li")

                # remove all "Untitled" episodes
                EPISODE_TEXT_CSS_SELECTOR = "div:nth-child(1) > div:nth-child(1)"
                item_text = items[0].find_element(
                    By.CSS_SELECTOR, EPISODE_TEXT_CSS_SELECTOR).text

                if not item_text:
                    logger.info("Empty episode title. Refreshing page...")
                    self.driver.refresh()
                    WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
                        EC.staleness_of(items[0]))
                    continue

                if "untitled" in item_text.lower():
                    logger.info("Removing draft episode")
                    self.remove_episode(items[0])
                    continue

                if len(items) > keep_episodes_num:
                    last_episode_item = items[-1]

                    episode_title = last_episode_item.find_element(
                        By.CSS_SELECTOR, EPISODE_TEXT_CSS_SELECTOR).text

                    logger.info(f"Removing episode: {episode_title}")

                    self.remove_episode(last_episode_item)

                else:
                    keep_removing = False
            except SeleniumExceptions.StaleElementReferenceException:
                self.driver.get(URL)

    def remove_episode(self, item: webdriver.remote.webelement.WebElement):
        buttons = item.find_elements(By.CSS_SELECTOR, "button")

        if len(buttons):
            options_button = buttons[-1]
            options_button.click()

            delete_episode_button = WebDriverWait(
                self.driver, DEFAULT_TIMEOUT).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         f'//button[normalize-space()="Delete episode"]')))
            delete_episode_button.click()

            confirm_deletion_button = WebDriverWait(
                self.driver, DEFAULT_TIMEOUT
            ).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     f'//button[normalize-space()="Yes, delete this episode"]'
                     )))

            confirm_deletion_button.click()
        self.driver.refresh()

        WebDriverWait(self.driver,
                      DEFAULT_TIMEOUT).until(EC.staleness_of(item))
