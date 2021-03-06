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

    def __init__(self, driver, email, password, max_retries=5):
        self.driver = driver
        self.email = email
        self.password = password
        self.max_retries = max_retries

    def log_in(self):
        URL = ANCHOR_URL + "login"

        for retry_cnt in range(0, self.max_retries):
            try:
                logger.info(f"Loading page: {URL}")
                self.driver.get(URL)
                logger.info("Waiting for page elements to be ready")
                email_element = WebDriverWait(
                    self.driver, DEFAULT_TIMEOUT).until(
                        EC.presence_of_element_located((By.ID, 'email')))

                password_element = self.driver.find_element(By.ID, "password")

                logger.info("Inserting email")
                email_element.send_keys(self.email)

                logger.info("Inserting password")
                password_element.send_keys(self.password)

                password_element.send_keys(Keys.RETURN)

                WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
                    EC.staleness_of(password_element))

                WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
                    EC.title_contains("Dashboard"))
            except Exception as e:
                logger.warn(f"Exception : {repr(e)}")
                logger.info(f"Trying again ({retry_cnt}/{self.max_retries})")
            else:
                return

        raise RuntimeError("Max retries reached. Could not log in.")

    def upload_audio_file(self, audio_path):
        logger.info("Waiting for Upload file button to be available")

        input_file_div = WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[data-testid='dropzone']")))

        input_file = input_file_div.find_element(by=By.CSS_SELECTOR,
                                                 value="input:nth-child(1)")

        logger.info("Uploading audio file")

        self.driver.execute_script("arguments[0].style.display = 'block';",
                                   input_file)

        input_file.send_keys(audio_path)

        # wait for button with desc "Edit your audio"

        WebDriverWait(self.driver, DEFAULT_TIMEOUT * 3).until(
            EC.element_to_be_clickable(
                (By.XPATH, f'//a[normalize-space()="Edit your audio"]')))
        logger.info("Audio file upload finished")

    def upload_audio(self):
        URL = ANCHOR_URL + "dashboard/episode/new"

        for retry_cnt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"Loading Upload page ({retry_cnt}/{self.max_retries}): {URL}"
                )
                self.driver.get(URL)
                WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
                    EC.title_contains("Create"))

                logger.info("Waiting for Save button to be available")

                save_button = WebDriverWait(
                    self.driver, DEFAULT_TIMEOUT).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//button/div[text()="Save episode"]')))

                logger.info("Clicking on save button")
                save_button.click()
                WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
                    EC.staleness_of(save_button))

                logger.info("Waiting for Episode Options page.")
                WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
                    EC.text_to_be_present_in_element((By.XPATH, "//h1"),
                                                     "Episode options"))
            except Exception as e:
                logger.warn(f"Exception : {repr(e)}")
                logger.info(f"Trying again ({retry_cnt}/{self.max_retries})")
            else:
                return

        raise RuntimeError("Could not Upload episode.")

    def publish_episode(self, title, desc, audio_path):
        logger.info('Waiting for title and description fields to be ready')

        title_field = WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "title")))
        logger.info(f'Adding title: "{title}"')
        title_field.send_keys(title)

        desc_field = WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div[role="textbox"]')))
        # // Wait some time so any field refresh doesn't mess up with our input

        logger.info(f'Adding description: "{desc}"')
        desc_field.send_keys(desc)

        self.upload_audio_file(audio_path)

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

        WebDriverWait(self.driver,
                      DEFAULT_TIMEOUT).until(EC.staleness_of(desc_field))

        WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '//*[@id="wordpress-share-modal-title"]'),
                "Episode published"))

    def remove_episodes(self, keep_episodes_num):
        URL = ANCHOR_URL + "dashboard/episodes"

        logger.info("Removing Drafts and old Episodes")

        keep_removing = True
        reload_page = True

        while keep_removing:

            if reload_page:
                try:
                    logger.info(f"Loading Episodes page: {URL}")
                    self.driver.get(URL)

                    WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
                        EC.text_to_be_present_in_element(
                            (By.CSS_SELECTOR, "h1"), "Episodes"))

                    reload_page = False
                except SeleniumExceptions.TimeoutException:
                    logger.info("Page title not found. Refreshing page...")
                    continue

            EPISODE_LIST_CSS_SELECTOR = ".css-1ausnd5"
            EPISODE_TEXT_CSS_SELECTOR = "span"

            try:
                episodes_list = WebDriverWait(
                    self.driver, DEFAULT_TIMEOUT).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, EPISODE_LIST_CSS_SELECTOR)))

                items = episodes_list.find_elements(By.TAG_NAME, "tr")

                # Removing header from episodes count
                num_episodes = len(items) - 1
                head_item = items[1]

                # remove all "Untitled" episodes
                fields = head_item.find_elements(By.TAG_NAME, "span")

                if len(fields) != 0:
                    item_text = fields[0].text

                if not item_text:
                    logger.info("Empty episode title. Refreshing page...")
                    self.driver.refresh()
                    WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
                        EC.staleness_of(head_item))
                    continue

                if "untitled" in item_text.lower():
                    logger.info("Removing draft episode")
                    self._remove_episode(head_item)
                    continue

                if num_episodes > keep_episodes_num:
                    last_episode_item = items[-1]

                    fields = last_episode_item.find_elements(
                        By.CSS_SELECTOR, EPISODE_TEXT_CSS_SELECTOR)

                    if len(fields) != 0:
                        episode_title = fields[0].text
                        logger.info(f"Removing episode: {episode_title}")

                        self._remove_episode(last_episode_item)

                else:
                    keep_removing = False
            except SeleniumExceptions.StaleElementReferenceException:
                reload_page = True
            except SeleniumExceptions.TimeoutException:
                reload_page = True

    def _remove_episode(self, item: webdriver.remote.webelement.WebElement):
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
