#!/bin/sh -l
cd /data

pip install -r requirements.txt
python3 yt2anchor.py
