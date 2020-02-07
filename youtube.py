#!/usr/bin/env python
# -*- coding: utf-8 -*-

from globals import *
from apiclient.discovery import build 
from apiclient.errors import HttpError 
from oauth2client.tools import argparser 
from oauth2client.client import GoogleCredentials 

#setup youtube api
creds = GoogleCredentials.get_application_default()
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)  

def youtube_search(query,maxresults):
    #get title, thumbnail and video id
    search_response = youtube.search().list(
        q=query,
        type="video",
        part="id,snippet",
        maxResults=maxresults
    ).execute()

    #return first result
    if(maxresults==1):
        vidID = ""
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                vidID = search_result["id"]["videoId"]
        return vidID

    #return top 3 list
    else:
        #videos to get viewcount from
        videos = {}
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos[search_result["id"]["videoId"]] = search_result["snippet"]["title"]

        #get viewcount
        s = ','.join(videos.keys())
        videos_list_response = youtube.videos().list(
            id=s,
            part='id,statistics'
        ).execute()    
    
        res = []
        for i in videos_list_response['items']:
            temp_res = dict(v_id = i['id'], v_title = videos[i['id']])
            temp_res.update(i['statistics'])
            res.append(temp_res["viewCount"])
 
        res.sort(key=int)

        vidIDs = []
        i = 2
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                vidIDs.append(search_result["snippet"]["title"])
                vidIDs.append(search_result["snippet"]["thumbnails"]["default"]["url"])
                vidIDs.append(search_result["id"]["videoId"])
                vidIDs.append(res[i])
                i = i-1
        return vidIDs
