#!/usr/bin/env python
# -*- coding: utf-8 -*-

from globals import *
import requests

def sendFacebookMessage(user, msg):
    sendFacebookTypingOff(user)
    response = requests.post(
        url='https://graph.facebook.com/v{0}/me/messages?access_token={1}'.format(FACEBOOK_API, FACEBOOK_TOKEN),
        json={'messaging_type':'RESPONSE', 'recipient':{'id':user}, 'message':{'text':msg}}
    ).json()

def sendFacebookRaw(user, data):
    sendFacebookTypingOff(user)
    response = requests.post(
        url='https://graph.facebook.com/v{0}/me/messages?access_token={1}'.format(FACEBOOK_API, FACEBOOK_TOKEN),
        json=data
    ).json()
		
def sendFacebookSeen(user):
    response = requests.post(
        url='https://graph.facebook.com/v{0}/me/messages?access_token={1}'.format(FACEBOOK_API, FACEBOOK_TOKEN),
        json={'messaging_type':'RESPONSE', 'recipient':{'id':user}, 'sender_action':'mark_seen'}
    ).json()
    print(response)    
	
def sendFacebookTypingOn(user):
    response = requests.post(
        url='https://graph.facebook.com/v{0}/me/messages?access_token={1}'.format(FACEBOOK_API, FACEBOOK_TOKEN),
        json={'messaging_type':'RESPONSE', 'recipient':{'id':user}, 'sender_action':'typing_on'}
    ).json()
	
def sendFacebookTypingOff(user):
    response = requests.post(
        url='https://graph.facebook.com/v{0}/me/messages?access_token={1}'.format(FACEBOOK_API, FACEBOOK_TOKEN),
        json={'messaging_type':'RESPONSE', 'recipient':{'id':user}, 'sender_action':'typing_off'}
    ).json()
