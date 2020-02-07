#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function 
import urllib.request, urllib.parse, urllib.error 
import sys, datetime, json, re, random, requests
from _thread import start_new_thread
from subprocess import call 
from flask import Flask 
from flask import request 
from flask import make_response
from shutil import copyfile
import fileinput

#local imports
from globals import *

__author__ = "Dominik Fehr, Sebastian Schmeling"
__copyright__ = "Copyright 2017,2018 "+__author__
__credits__ = "Jürgen Waithera"
__license__ = "Internal"
__version__ = "26.03.2018"
__maintainer__ = "Dominik Fehr"
__email__ = "df@legit-it.de"
__status__ = "Development"

app = Flask(__name__) 

@app.route('/ddl', methods=['GET'])
def ddl():
    #print(str(request.headers))
    print(request.args.get('key'))
    return str(request)

@app.route('/mbot', methods=['POST'])
def webhook():

    global CURRENT_USER_ID
    global CURRENT_SONG_ID
    global CURRENT_SONG_URL
    global CURRENT_USER_NAME
    global CURRENT_LOOP_RESULT    

    #check auth
    if(request.headers['token']!='apiai'):
        res = {
            "speech": "ERROR - T0ken not where it should be!",
            "source": "Tunes2u"
        }
        res = json.dumps(res, indent=4)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        return r

    #get important variables from input
    req = request.get_json(silent=True, force=True) 
    query = req.get('result').get('resolvedQuery')
    lang = req.get('lang')
    messenger = req.get('originalRequest').get('source')
    if(messenger=="telegram"):
        CURRENT_USER_ID = req.get('originalRequest').get('data').get('message').get('chat').get('id')
    elif(messenger=="facebook"):
        CURRENT_USER_ID = req.get('originalRequest').get('data').get('sender').get('id')

    #logging and debugging
    if(DEBUG==1):
        print(str(req).encode('utf-8'))
        print("Messenger is: "+messenger)
        print("User ID: "+str(CURRENT_USER_ID))
        print("Language is: "+str(lang))
        print("Final Query is: '" + query +"'")
    if(LOG==1):
        with open("search.log", "a") as logfile:
            logfile.write(time.strftime("%d/%m/%Y %H:%M:%S")+" - "+str(CURRENT_USER_ID)+" - "+str(messenger)+" - "+query+"\n")

    #let user know we received the message
    if(messenger == "facebook"):
        sendFacebookSeen(CURRENT_USER_ID)
			
    #try get name and add to db if not existing
    try:
        if(messenger == "facebook"):
            CURRENT_USER_NAME = get_user_name(CURRENT_USER_ID, messenger, lang)
        elif(messenger == "telegram"):
            CURRENT_USER_NAME = req.get('originalRequest').get('data').get('message').get('chat').get('first_name')
            get_user_name(CURRENT_USER_ID, messenger, lang)
    except:
        CURRENT_USER_NAME = " "

    #look for cmd in query
    if ("_WELCOME" in query):
        requestType = "initial"
    elif (query.lower() == "hilfe" or query.lower() == "help"):
        requestType = "help"
    elif (query[0:6].lower() == "liste "):
        query = query[6:]
        requestType = "list"
    elif (query[0:5].lower() == "list "):
        query = query[5:]
        requestType = "list"
    elif (query[0:6].lower() == "video "):
        query = query[6:]
        requestType = "video"
    else:
        requestType = "default"

    #check if query is yt url or normal query
    if (requestType != "initial"):
        if ("/watch?v=" not in query) and ("youtu.be/" not in query) and ((requestType == "default") or (requestType == "video")):
            CURRENT_SONG_URL = "https://www.youtube.com/watch?v="+youtube_search(query,1)
        elif ("/watch?v=" not in query) and ("youtu.be/" not in query) and (requestType == "list"):
            vidIDs = youtube_search(query,3)
        else:
            CURRENT_SONG_URL = query

    CURRENT_LOOP_RESULT = 0

    #prepare first best result
    if(requestType == "default" or requestType == "video"):
        #get video metadata
        try:
            prey_opts = {
                'quiet' : True
            }
            with youtube_dl.YoutubeDL(prey_opts) as preydl:
                meta = preydl.extract_info(CURRENT_SONG_URL, download=False)
                tmpSongId = meta['title'].replace(' ', '_')
                duration = (meta['duration'])
                CURRENT_SONG_ID = re.sub('[^a-zA-Z0-9-_*.]', '', tmpSongId)
        except:
            duration = 0
            print("Video unavailable")

        #generate first response
        if(duration == 0):
            waitResponse = ""
            if("de" in lang):
                print("de lang and " + messenger)
                if(messenger == "facebook"):
                    sendFacebookMessage(CURRENT_USER_ID, random.choice(ERROR_2_DE))
                elif(messenger == "telegram"):
                    sendFacebookMessage(CURRENT_USER_ID, random.choice(ERROR_2_DE))
            else:
                if(messenger == "facebook"):
                    sendTelegramMessage(CURRENT_USER_ID, random.choice(ERROR_2_EN))
                elif(messenger == "telegram"):
                    sendTelegramMessage(CURRENT_USER_ID, random.choice(ERROR_2_EN))

        elif (duration <= 600):
            if(requestType == "default"):
                start_new_thread(dlAndConvert,(CURRENT_USER_ID, CURRENT_SONG_ID, CURRENT_SONG_URL, messenger,"audio",lang,))
            if(requestType == "video"):
                start_new_thread(dlAndConvert,(CURRENT_USER_ID, CURRENT_SONG_ID, CURRENT_SONG_URL, messenger,"video",lang,))
            if("de" in lang):
                waitResponse = random.choice(WAIT_1_DE)+" "+CURRENT_USER_NAME+random.choice(WAIT_2_DE)
            else:
                waitResponse = random.choice(WAIT_1_EN)+" "+CURRENT_USER_NAME+random.choice(WAIT_2_EN)   

        elif (duration > 600) and (duration <= 1200):
            if(requestType == "default"):
                start_new_thread(dlAndConvert,(CURRENT_USER_ID, CURRENT_SONG_ID, CURRENT_SONG_URL, messenger,"audio",lang,))
            if(requestType == "video"):
                start_new_thread(dlAndConvert,(CURRENT_USER_ID, CURRENT_SONG_ID, CURRENT_SONG_URL, messenger,"video",lang,))
            if("de" in lang):
                waitResponse = random.choice(WAITLONG_1_DE)+" "+CURRENT_USER_NAME+random.choice(WAITLONG_2_DE)
            else:
                waitResponse = random.choice(WAITLONG_1_EN)+" "+CURRENT_USER_NAME+random.choice(WAITLONG_2_EN)
   
        elif(duration > 1200):
            if("de" in lang):
                waitResponse = random.choice(TOOLONG_1_DE)+" "+CURRENT_USER_NAME+random.choice(TOOLONG_2_DE)
            else:
                waitResponse = random.choice(TOOLONG_1_EN)+" "+CURRENT_USER_NAME+random.choice(TOOLONG_2_EN)

        else:
            if("de" in lang):            
                waitResponse = random.choice(ERROR_1_DE)
            else:
                waitResponse = random.choice(ERROR_1_EN)

        #additional data
        facebook_message = {
            "text":waitResponse
        }
        telegram_message = {
            "text":waitResponse
        }

    #prepare top 3 list result
    elif(requestType == "list" and messenger != "telegram"):
        if("de" in lang):
            waitResponse = random.choice(LIST_1_DE)+" "+CURRENT_USER_NAME+random.choice(LIST_2_DE)
        else:
            waitResponse = random.choice(LIST_1_EN)+" "+CURRENT_USER_NAME+random.choice(LIST_2_EN)

        #additional data
        if(messenger == "facebook"):
            facebook_message = {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "list",
                        "elements": [
                            {
                                "title": vidIDs[0],
                                "image_url": vidIDs[1],
                                "subtitle": format(int(vidIDs[3]), ',d') + " Views !!!",
                                "default_action": {
                                    "type": "web_url",
                                    "url": "https://youtube.com/watch?v="+vidIDs[2],
                                    "messenger_extensions": "true",
                                    "webview_height_ratio": "compact",
                                    "fallback_url": "https://youtube.com/watch?v="+vidIDs[2]
                                },
                                "buttons": [
                                    {
                                        "type":"postback",
                                        "title":"Download #1",
                                        "payload":vidIDs[0]
                                    }
                                ]
                            },
                            {
                                "title": vidIDs[4],
                                "image_url": vidIDs[5],
                                "subtitle":  format(int(vidIDs[7]), ',d') + " Views !!",
                                "default_action": {
                                    "type": "web_url",
                                    "url": "https://youtube.com/watch?v="+vidIDs[6],
                                    "messenger_extensions": "true",
                                    "webview_height_ratio": "compact",
                                    "fallback_url": "https://youtube.com/watch?v="+vidIDs[6]
                                },
                                "buttons": [
                                    {
                                        "type":"postback",
                                        "title":"Download #2",
                                        "payload":vidIDs[4]
                                    }
                                ]
                            },
                            {
                                "title": vidIDs[8],
                                "image_url": vidIDs[9],
                                "subtitle":  format(int(vidIDs[11]), ',d') + " Views !",
                                "default_action": {
                                    "type": "web_url",
                                    "url": "https://youtube.com/watch?v="+vidIDs[10],
                                    "messenger_extensions": "true",
                                    "webview_height_ratio": "compact",
                                    "fallback_url": "https://youtube.com/watch?v="+vidIDs[10]
                                },
                                "buttons": [
                                    {
                                        "type":"postback",
                                        "title":"Download #3",
                                        "payload":vidIDs[8]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        telegram_message = {}

    elif (requestType == "initial"):
        waitResponse = ""
        facebook_message = {
            "attachment" : {
                "type" : "",
                "payload" : {
                    "sender_action" : "typing_on"
                }
            }
        }
        telegram_message = {}
        if("de" in lang):
            sendFacebookMessage(CURRENT_USER_ID,"Hey "+CURRENT_USER_NAME+random.choice(WELCOME_1_DE))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(WELCOME_2_DE))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(WELCOME_3_DE))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(WELCOME_4_DE))
        else:
            sendFacebookMessage(CURRENT_USER_ID,"Hey "+CURRENT_USER_NAME+random.choice(WELCOME_1_EN))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(WELCOME_2_EN))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(WELCOME_3_EN))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(WELCOME_4_EN))

    elif (requestType == "help"):
        waitResponse = ""
        facebook_message = {
            "attachment" : {
                "type" : "",
                "payload" : {
                    "sender_action" : "typing_on"
                }
            }
        }
        telegram_message = {}
        if("de" in lang):
            sendFacebookMessage(CURRENT_USER_ID,"Hey "+CURRENT_USER_NAME+random.choice(HELP_1_DE))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_2_DE))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_3_DE))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_4_DE))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_5_DE))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_6_DE))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_7_DE))
        else:
            sendFacebookMessage(CURRENT_USER_ID,"Hey "+CURRENT_USER_NAME+random.choice(HELP_1_EN))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_2_EN))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_3_EN))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_4_EN))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_5_EN))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_6_EN))
            time.sleep(0.25)
            sendFacebookMessage(CURRENT_USER_ID,random.choice(HELP_7_EN))

    res = {
        "speech": waitResponse,
        "displayText": waitResponse,
        "data": {"telegram": telegram_message, "facebook": facebook_message},
        "source": "Tunes2u"
    }

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    if (DEBUG==1):
        print("Returning... "+res)
    return r  

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting Tunes2U Server on port %d" % port)
    app.run(threaded=True, debug=False, port=port, host='0.0.0.0')
