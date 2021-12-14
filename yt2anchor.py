import os
import logging
import json

from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from dotenv import dotenv_values
from selenium import webdriver

from anchorfm_helper import AnchorFmHelper
import yt_helper

logger = logging.getLogger("YT_2_ANCHOR")

# using dotenv for local tests
config = dotenv_values(".env")

if config:
    ANCHOR_EMAIL = config['ANCHOR_EMAIL']
    ANCHOR_PASSWORD = config['ANCHOR_PASSWORD']
    EPISODE_PATH = config['EPISODE_PATH']
    KEEP_EPISODES_NUM = int(config['KEEP_EPISODES_NUM'])
else:
    ANCHOR_EMAIL = os.getenv('ANCHOR_EMAIL', "")
    ANCHOR_PASSWORD = os.getenv('ANCHOR_PASSWORD', "")
    EPISODE_PATH = os.getenv('EPISODE_PATH', "./")
    KEEP_EPISODES_NUM = int(os.getenv('KEEP_EPISODES_NUM', '0'))

EPISODE_JSON = 'episode.json'


def cleanup(filename):
    if os.path.exists(filename):
        os.remove(filename)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s  [%(levelname)s]: %(message)s",
                        level=logging.INFO)

    empty_anchor_vars = False

    if not ANCHOR_EMAIL:
        logger.error("Empty ANCHOR_EMAIL")
        empty_anchor_vars = True

    if not ANCHOR_PASSWORD:
        logger.error("Empty ANCHOR_PASSWORD")
        empty_anchor_vars = True

    if empty_anchor_vars:
        exit(1)

    cleanup(yt_helper.DEFAULT_AUDIO_FILENAME)

    episode_path = os.path.join(os.path.abspath(EPISODE_PATH), EPISODE_JSON)

    logger.info(f"Loading {episode_path}")

    episodeInfo = None
    with open(episode_path) as f:
        episodeInfo = json.load(f)

    ytVideoInfo = yt_helper.getVideoInfo(episodeInfo["id"])
    # Merge video info from YouTube and Episode file
    videoInfo = yt_helper.treat_episode_json(episodeInfo, ytVideoInfo)
    audioPath = yt_helper.download_audio(ytVideoInfo)

    # Using firefox driver so we don't have problems with emoji
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    serviceDriver = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=serviceDriver, options=options)

    try:
        anchor = AnchorFmHelper(driver, ANCHOR_EMAIL, ANCHOR_PASSWORD)
        anchor.logging_anchor()
        anchor.upload_audio(audioPath)
        anchor.publish_episode(videoInfo['title'], videoInfo['description'])

        if KEEP_EPISODES_NUM is not None and KEEP_EPISODES_NUM > 0:
            anchor.remove_episodes(KEEP_EPISODES_NUM)

    finally:
        driver.quit()
        cleanup(yt_helper.DEFAULT_AUDIO_FILENAME)
