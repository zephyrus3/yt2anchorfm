import logging
import yt_dlp
import json
import os

logger = logging.getLogger("YT_HELPER")
YT_URL = 'https://www.youtube.com/watch?v='
DEFAULT_AUDIO_FILENAME = 'episode.mp3'


def treat_episode_json(episodeInfo, episodeYtInfo):
    logger.info("Treating Episode Info")

    get_value = lambda key, infoLocal, infoYT: infoLocal[
        key] if key in infoLocal and infoLocal[key] else infoYT[key]

    id = get_value("id", episodeInfo, episodeYtInfo)
    title = get_value("title", episodeInfo, episodeYtInfo)
    desc = get_value("description", episodeInfo, episodeYtInfo)

    return {
        "id": id,
        "title": title if title else "No Title",
        "description": desc if desc else "No Description"
    }


def getVideoInfo(video_id):
    logger.info(f"Getting video ({video_id}) info")
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(YT_URL + video_id, download=False)
        return info


def download_audio(video_info):
    ydl_opts = {
        'format':
        'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger':
        logger,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logger.info("Downloading video and converting audio")
        ret = ydl.download([YT_URL + video_info['id']])

        if ret == 0:
            logger.info("Renaming episode audio file")
            os.rename(f"{video_info['title']} [{video_info['id']}].mp3",
                      DEFAULT_AUDIO_FILENAME)
            return os.path.abspath(DEFAULT_AUDIO_FILENAME)

        raise Exception(f"Youtube Video download failed with error: {ret}")
