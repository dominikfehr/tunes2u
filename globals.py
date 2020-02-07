#!/usr/bin/env python
# -*- coding: utf-8 -*-

FACEBOOK_API = "2.12"
TELEGRAM_TOKEN = "INSERT"
FACEBOOK_TOKEN = "INSERT"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

CURRENT_MSGR_ID = "unknown"
CURRENT_USER_ID = 0
CURRENT_LOOP_RESULT = 0
CURRENT_SONG_ID = "unknown"
CURRENT_USER_NAME = ""
CURRENT_SONG_URL = "https://www.youtube.com"
CURRENT_TYPE_ID = "unknown"
CURRENT_LANG_ID = ""
DEBUG = 1
LOG = 1

from texts import *
from youtube import *
from facebook import *
from telegram import *
from database import *
from fileio import *
from converter import *
