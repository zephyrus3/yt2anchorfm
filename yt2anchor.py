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
else:
    ANCHOR_EMAIL = os.getenv('ANCHOR_EMAIL', "")
    ANCHOR_PASSWORD = os.getenv('ANCHOR_PASSWORD', "")

EPISODE_JSON = 'episode.json'


def cleanup(filename):
    if os.path.exists(filename):
        os.remove(filename)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s  [%(levelname)s]: %(message)s",
                        level=logging.INFO)

    cleanup(yt_helper.DEFAULT_AUDIO_FILENAME)

    logger.info(f"Loading {EPISODE_JSON}")

    episodeInfo = None
    with open(EPISODE_JSON) as f:
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
        anchor.loggin_anchor()
        anchor.upload_audio(audioPath)
        anchor.fill_episode_data(videoInfo['title'], videoInfo['description'])
    finally:
        driver.quit()
        cleanup(yt_helper.DEFAULT_AUDIO_FILENAME)
