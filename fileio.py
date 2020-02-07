#!/usr/bin/env python
# -*- coding: utf-8 -*-

from globals import *
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import pyinotify
import time, os

def wait_for_file_creation(filename, userId, songId, songUrl, msgrId, type, lang):
    global CURRENT_LOOP_RESULT
    global CURRENT_USER_ID
    global CURRENT_SONG_ID
    global CURRENT_SONG_URL
    global CURRENT_MSGR_ID
    global CURRENT_TYPE_ID
    global CURRENT_LANG_ID

    CURRENT_USER_ID = userId
    CURRENT_SONG_ID = songId
    CURRENT_SONG_URL = songUrl
    CURRENT_MSGR_ID = msgrId
    CURRENT_TYPE_ID = type
    CURRENT_LANG_ID = lang
    CURRENT_LOOP_RESULT = 0
	
    wm = pyinotify.WatchManager()
    eh = MyEventHandler()
    wm.add_watch(filename, pyinotify.ALL_EVENTS, rec=True)
    notifier = pyinotify.Notifier(wm, eh)
    if(DEBUG==1):
        print(str(userId) + " waits for " + filename + "...")
    while (CURRENT_LOOP_RESULT!=1):
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except:
            e = sys.exc_info()
            if(DEBUG==1):
                print(str(e)) 
            break
    if(DEBUG==1):
        print("Stopping watcher for: "+filename)
    notifier.stop()

class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        global CURRENT_LOOP_RESULT
        global CURRENT_USER_ID
        global CURRENT_SONG_ID
        global CURRENT_SONG_URL
        global CURRENT_MSGR_ID
        global CURRENT_LANG_ID

        CURRENT_LOOP_RESULT = 1
        if(DEBUG==1):
            print("Got it! Checking...")
        checkFileAndReturn(CURRENT_USER_ID, CURRENT_SONG_ID, CURRENT_SONG_URL, CURRENT_MSGR_ID, "audio", CURRENT_LANG_ID)

def checkFileAndReturn(userId, songId, songUrl, msgrId, filetype, lang):
    if(filetype == "audio"):
        file = "./mp3/"+songId+".mp3"
    elif(filetype == "video"):
        file = "./mp3/"+songId+".mp4"

    imgfile = "./mp3/"+songId+".jpg"

    #add id3 tags
    if(filetype == "audio"):
        if(DEBUG==1):
            print("Writing IDv3 tag...")
        audio = EasyID3(file)
        audio['title'] = songId.replace('_',' ')
        audio['artist'] = "DJ Tuner"
        audio['album'] = "Tunes2u.com"
        audio.save()

        #add id3 image
        try:
            a = MP3(file, ID3=ID3)
            with open(imgfile, 'br') as f:
                contents = f.read()
            a.tags.add(APIC(encoding=3, mime=u'image/jpg', type=3, desc=u'Albumcover', data=contents))
            a.save()
        except:
            if(DEBUG==1):
                print("IMG for ID3 not found...")
	
    if(filetype=="audio"):
        if(DEBUG==1):
            print("Returning audio file...")
		
        if(msgrId=="telegram"):
            data={'chat_id': userId, 'text': 'https://tunes2u.com/'+songId+'.mp3'}
            sendTelegramRaw(userId,data)
        elif(msgrId=="facebook"):
            if("de" in lang):
                data={'recipient':{'id': userId}, 'message':{'attachment':{'type':'template','payload':{'template_type':'generic','elements':[{'title':songId.replace('_',' '),'image_url':'https://tunes2u.com/'+songId+'.jpg','default_action':{'type':'web_url','url':songUrl,'messenger_extensions':'true','webview_height_ratio':'compact'},'buttons':[{'type':'web_url','url':'https://tunes2u.com/tune4u.php?file='+songId+'.mp3','title':'Download MP3'},{'type':'postback','title':'Video suchen...','payload':'video '+songId.replace('_',' ')},{'type':'element_share'}]}]}}}}
            else:
                data={'recipient':{'id': userId}, 'message':{'attachment':{'type':'template','payload':{'template_type':'generic','elements':[{'title':songId.replace('_',' '),'image_url':'https://tunes2u.com/'+songId+'.jpg','default_action':{'type':'web_url','url':songUrl,'messenger_extensions':'true','webview_height_ratio':'compact'},'buttons':[{'type':'web_url','url':'https://tunes2u.com/tune4u.php?file='+songId+'.mp3','title':'Download MP3'},{'type':'postback','title':'Search video...','payload':'video '+songId.replace('_',' ')},{'type':'element_share'}]}]}}}}
			
            sendFacebookRaw(userId,data)

    if(filetype=="video"):
        if(DEBUG==1):
            print("Returning video file...")
	
        if(msgrId=="telegram"):
            data={'chat_id': userId, 'text': 'https://tunes2u.com/'+songId+'.mp4'}
            sendTelegramRaw(userId,data)
        elif(msgrId=="facebook"):
            if("de" in lang):
                data={'recipient':{'id': userId}, 'message':{'attachment':{'type':'template','payload':{'template_type':'generic','elements':[{'title':songId.replace('_',' '),'image_url':'https://tunes2u.com/'+songId+'.jpg','default_action':{'type':'web_url','url':songUrl,'messenger_extensions':'true','webview_height_ratio':'compact'},'buttons':[{'type':'web_url','url':'https://tunes2u.com/tune4u.php?file='+songId+'.mp4','title':'Download MP4'},{'type':'postback','title':'MP3 suchen...','payload':songId.replace('_',' ')},{'type':'element_share'}]}]}}}}
            else:
                data={'recipient':{'id': userId}, 'message':{'attachment':{'type':'template','payload':{'template_type':'generic','elements':[{'title':songId.replace('_',' '),'image_url':'https://tunes2u.com/'+songId+'.jpg','default_action':{'type':'web_url','url':songUrl,'messenger_extensions':'true','webview_height_ratio':'compact'},'buttons':[{'type':'web_url','url':'https://tunes2u.com/tune4u.php?file='+songId+'.mp4','title':'Download MP4'},{'type':'postback','title':'Search MP3...','payload':songId.replace('_',' ')},{'type':'element_share'}]}]}}}}
			
            sendFacebookRaw(userId,data)
			
    #check total searches and send tips or ads depending on it
    tip = check_total_searches(userId, lang)
    
    if(tip != "notip"):
        if(msgrId=="telegram"):
            sendTelegramMessage(userId,tip)
        elif(msgrId=="facebook"):
            sendFacebookMessage(userId,tip)
    else:
        if(DEBUG==1):
            print("No tip to be returned...")

    #check if old files should be removed
    clear_cache()
	
def check_total_searches(userid, lang):
    totalSearches = get_user_searches_count(userid)
    
    try:
        if("de" in lang):
            return TIP_LINKS_DE[totalSearches]
        else:
            return TIP_LINKS_EN[totalSearches]    
    except:
        return "notip"
	
def clear_cache():
    #search and clear mp3's older than 5mins
    now = time.time()
    cutoff = now - (300)
    files = os.listdir("mp3/")
    for xfile in files:
        if "1.png" not in xfile and "tune4u.php" not in xfile and "index.php" not in xfile and "getfile.php" not in xfile:
            if os.path.isfile( "mp3/" + xfile ):
                t = os.stat( "mp3/" + xfile )
                c = t.st_ctime
                if c < cutoff:
                    os.remove("mp3/" + xfile)
