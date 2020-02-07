#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals 
import os, youtube_dl
from globals import *
from _thread import start_new_thread
from pathlib import Path

class MyLogger(object):
    global CURRENT_MSGR_ID
    global CURRENT_LANG_ID
    global CURRENT_USER_ID

    def debug(self, msg):
        if(DEBUG==1):
            print(msg)
        pass

    def warning(self, msg):
        if(DEBUG==1):
            print(msg)
        pass

    def error(self, msg):
        print("HERE")
        if(CURRENT_MSGR_ID=="telegram"):
            if("de" in CURRENT_LANG_ID):
                sendTelegramMessage(CURRENT_USER_ID, ERROR_1_DE)
            else:
                sendTelegramMessage(CURRENT_USER_ID, ERROR_1_EN)                
        elif(CURRENT_MSGR_ID=="facebook"):
            if("de" in CURRENT_LANG_ID):
                sendFacebookMessage(CURRENT_USER_ID, ERROR_1_DE)
            else:
                sendFacebookMessage(CURRENT_USER_ID, ERROR_1_EN)   

        print(msg)

def dlAndConvert(userId, songId, songUrl, msgrId, type, lang):
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

    if(type == "audio"):
        if(DEBUG==1):
            print("Trying to download audio...")	
		
	#check if file already exists
        audio_file = Path('mp3/'+songId+'.mp3')
        if audio_file.is_file():
            if(DEBUG==1):
                print("MP3 already exists...")
            start_new_thread(checkFileAndReturn,(CURRENT_USER_ID, CURRENT_SONG_ID, CURRENT_SONG_URL, CURRENT_MSGR_ID, "audio", lang,))
            return
		
        #touch for notifier to follow
        open('mp3/'+songId+'.mp3', 'a').close()

        #set download options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'mp3/'+songId+'.%(ext)s',
            'cachedir': False,
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'prefer_ffmpeg' : True,
            'writethumbnail': True,
            'postprocessors': [
	        {
                'key': 'FFmpegExtractAudio',
	            'preferredcodec': 'mp3',
	            'preferredquality': '192',
	        },
            ],
            'logger': MyLogger(),
	        'progress_hooks': [my_hook],
        }
	
    elif(type == "video"):
        if(DEBUG==1):
            print("Trying to download video...")	
		
		#check if file already exists
        video_file = Path('mp3/'+songId+'.mp4')
        if video_file.is_file():
            if(DEBUG==1):
                print("MP4 already exists...")
            start_new_thread(checkFileAndReturn,(CURRENT_USER_ID, CURRENT_SONG_ID, CURRENT_SONG_URL, CURRENT_MSGR_ID, "video", lang,))
            return
			
		#set download options
        ydl_opts = {
            'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': 'mp3/'+songId+'.%(ext)s',
            'cachedir': False,
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'prefer_ffmpeg' : True,
            'writethumbnail': True,
            'logger': MyLogger(),
	        'progress_hooks': [my_hook],
        }
		
    #download and convert video
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([songUrl])
		
def my_hook(d):
    global CURRENT_USER_ID
    global CURRENT_SONG_ID
    global CURRENT_SONG_URL
    global CURRENT_MSGR_ID
    global CURRENT_TYPE_ID
    global CURRENT_LANG_ID

    #youtube video download finished
    if d['status'] == 'finished':
        if(DEBUG==1):
            print("Download finished!")	
        mp3file, file_extension = os.path.splitext(d['filename'])
        if(CURRENT_TYPE_ID == "audio"):
            start_new_thread(wait_for_file_creation,(mp3file+".mp3",CURRENT_USER_ID, CURRENT_SONG_ID, CURRENT_SONG_URL, CURRENT_MSGR_ID, "audio", CURRENT_LANG_ID,))
        elif(CURRENT_TYPE_ID == "video" and file_extension == ".m4a"):
            start_new_thread(checkFileAndReturn,(CURRENT_USER_ID, CURRENT_SONG_ID, CURRENT_SONG_URL, CURRENT_MSGR_ID, "video", CURRENT_LANG_ID,))
