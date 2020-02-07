#!/usr/bin/env python
# -*- coding: utf-8 -*-

from globals import *
import requests

def sendTelegramMessage(user, msg):
	requests.post(
		url='https://api.telegram.org/bot{0}/{1}'.format(TELEGRAM_TOKEN, "sendMessage"),
		json={'chat_id': user, 'text': msg}
	).json()
	
def sendTelegramRaw(user, data):
        print("test")
        requests.post(
		url='https://api.telegram.org/bot{0}/{1}'.format(TELEGRAM_TOKEN, "sendMessage"),
		json=data
	).json()
