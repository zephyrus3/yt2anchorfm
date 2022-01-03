#!/bin/sh -l
cd /data || exit 1

pip install -r requirements.txt
python3 yt2anchor.py
