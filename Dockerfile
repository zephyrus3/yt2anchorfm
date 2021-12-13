FROM python:3.8-alpine

RUN apk update && apk add build-base libffi-dev ffmpeg firefox \
&& mkdir /data

COPY anchorfm_helper.py /data/anchorfm_helper.py
COPY yt2anchor.py /data/yt2anchor.py
COPY yt_helper.py /data/yt_helper.py
COPY requirements.txt /data/requirements.txt

COPY entrypoint.sh /data/entrypoint.sh

RUN chmod 777 /data/entrypoint.sh
ENV LC_ALL=en_US.UTF-8

ENTRYPOINT [ "/data/entrypoint.sh" ]
