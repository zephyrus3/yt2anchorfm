# yt2anchorfm

yt2anchorfm is an python module to upload an audio file from a given youtube video automatically to your Anchor.fm account.

yt2anchorfm was inspired by [Schrodinger-Hat/youtube-to-anchorfm](https://github.com/Schrodinger-Hat/youtube-to-anchorfm)

## How it works

### Workflow

1. Read `episode.json` to get the Youtube video ID
2. Using [yt_dlp](https://github.com/yt-dlp/yt-dlp), we get the video info (title and description), download the video and convert it to an audio file.
3. Merge `episode.json` and the video info
4. Using [selenium](https://github.com/SeleniumHQ/selenium) and some environment vars, we log in to the Anchor.fm, upload the audio, and fill the title and description from step 3.
5. If it is the case, we remove old episodes and drafts, keeping the latest X episodes.

### Episode format

As input, we use the `episode.json` file as input. This file can have the following fields:

- `id` **(required)**: The id of the Youtube video. E.g., for the video link https://youtu.be/Wk47JOy3FNg, the last part, `Wk47JOy3FNg`, is the id.
- `title` (optional) : The title used on the episode. If empty or not found, the Youtube video title will be used.
- `description` (optional) : The description used on the episode. If empty or not found, the Youtube video description will be used.

Both `title` and `description` accepts emoji on them.

```
{
  "id": "Wk47JOy3FNg",
  "title": "yt2anchorfm is the best ⭐"
  "description" : "😍 yt2anchorfm RULES!!! 😍"
}
```

### Variables

- `ANCHOR_EMAIL` **(required)**: Email used to log in to  Anchor.fm
- `ANCHOR_PASSWORD` **(required)**: Password used to log in to Anchor.fm
- `EPISODE_PATH` (optional): Path used inside the container environment that points to the cloned repo. Usually you don't want to change this.
- `KEEP_EPISODES_NUM` (optional): Number of episodes to keep after an upload. Drafts and older episodes will be deleted if this value is greater than zero. The default value is zero.

For GitHub Action, to keep you Anchor credential safe, you should use `ANCHOR_EMAIL` and `ANCHOR_PASSWORD` as [encrypted secrets](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets#creating-encrypted-secrets-for-a-repository).

For Local and Docker uses, recommend using the `.env` file as it is simpler and can also be used fro both environments.

`.env` file example:
```.env
ANCHOR_EMAIL=myemail@email.com
ANCHOR_PASSWORD=p4ssw0rd
EPISODE_PATH=./
KEEP_EPISODES_NUM=2
```

### GitHub Action
The action uses a composite action to have both python, geckodriver and ffmpeg configured. The whole process of downloading the video, converting video to audio format and uploading it to Anchor.fm takes ~3 min.

In your repository root directory you should add a `episode.json`. Any changes on this file will trigger the action.

Then you can add under the `.github/workflows` directory this file:

main.yml
```yml
name: 'yt2anchorfm - Upload Episode'

on:
  push:
    paths: 
      - episode.json
    branches: [main]

jobs:
  upload_episode:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2
      - name: yt2anchorfm - Upload Episode from YouTube To Anchor.Fm
        uses: zephyrus3/yt2anchorfm@main
        with:
          anchor_email: ${{ secrets.ANCHOR_EMAIL }}
          anchor_password: ${{ secrets.ANCHOR_PASSWORD }}
```

### Local

We recommend using a [virtual environment](https://docs.python.org/pt-br/3/library/venv.html) to install the requirements.

```sh
pip install venv
python -m venv venv

# On Linux
source venv/bin/activate

# On Windows
venv/Scripts/Activate.bat

pip install -r requirements.txt

# Run
python yt2anchor.py
```

The [yt_dlp](https://github.com/yt-dlp/yt-dlp) depends on ffmpeg to convert the YouTube videos into audio files, so be sure to install it beforehand.

### Docker
For docker runs, you just need to setup the `.env` file and the `episode.json`. By using `docker-compose` and the provided files (yt2anchor_alpine.yml/yt2anchor_ubuntu.yml) you can easily build the image and run the container:

```sh
# the docker-compose files already have instructions to build the image
docker-compose -f yt2anchor_ubuntu.yml up
# or
docker-compose -f yt2anchor_alpine.yml up
```

# License
MIT
