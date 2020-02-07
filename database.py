#!/usr/bin/env python
# -*- coding: utf-8 -*-

from globals import *
import pymysql as PyMySQL
import requests
from _thread import start_new_thread
import sys, time

def get_user_name(userid, channel, lang):
    #Get username from db if it exists else create it
    global DEBUG
    username = ""

    try:
        #setup mysql connection
        db = PyMySQL.connect("localhost", "tuner", "tunerpassword?", "tunes2u")

        cursor = db.cursor(PyMySQL.cursors.DictCursor)
        cursor.execute("SELECT firstname FROM users WHERE channel_userid = '" + str(userid) + "';")
        if(cursor.rowcount == 0):
            if(channel == "facebook"):
                data = requests.get(url='https://graph.facebook.com/v{0}/{2}?fields=first_name,last_name,locale&access_token={1}'.format(FACEBOOK_API, FACEBOOK_TOKEN, userid)).json()
                username = data["first_name"]
                start_new_thread(add_user_to_db,({"firstname": data["first_name"], "lastname": data["last_name"], "locale": data["locale"], "channel": channel, "userid": userid},))
                if(DEBUG == 1):
                    print("Username from GET is: " + username)
            elif(channel == "telegram"):
                start_new_thread(add_user_to_db,({"firstname": username, "lastname": "", "locale": lang, "channel": channel, "userid": userid},))
        else:
            if(channel == "facebook"):
                username = cursor.fetchone()["firstname"]
            cursor.execute("UPDATE users SET lastsearch = NOW(), totalsearches = totalsearches + 1 WHERE channel_userid = '" + str(userid) + "';")
            db.commit()
            if(DEBUG == 1):
                print("Username from DB is: " + username)
        cursor.close()
        db.close()
    except:
        e = sys.exc_info()
        with open("error.log", "a") as logfile:
            logfile.write(time.strftime("%d/%m/%Y %H:%M:%S")+" - "+str(e)+"\n")
        db.rollback()
        db.close()

    return username

def get_user_searches_count(userid):
    try:
        # Setup MySQL connection
        db = PyMySQL.connect("localhost", "tuner", "tunerpassword?", "tunes2u")

        # Get users total count of searches
        cursor = db.cursor(PyMySQL.cursors.DictCursor)
        cursor.execute("SELECT totalsearches FROM users WHERE channel_userid = '" + str(userid) + "';")
        value =  int(cursor.fetchone()["totalsearches"])
        cursor.close()
        db.close()

        return value
    except:
        e = sys.exc_info()
        with open("error.log", "a") as logfile:
            logfile.write(time.strftime("%d/%m/%Y %HH:%M:%S") + " - " + str(e) +"\n")
        db.close()

def add_user_to_db(data):
    try:
        #setup mysql connection
        db = PyMySQL.connect("localhost", "tuner", "tunerpassword?", "tunes2u")

        # Add user to db
        cursor = db.cursor(PyMySQL.cursors.DictCursor)
        cursor.execute("SELECT id FROM channels WHERE name = '" + data["channel"] + "';")
        channelid = cursor.fetchone()["id"]

        # Check if formating is enough escaping
        if(DEBUG==1):
            print("Adding to DB: "+str(data))

        cursor.execute("INSERT INTO users(firstname, lastname, locale, channel, channel_userid) VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\")".format(data["firstname"], data["lastname"], data["locale"], channelid, data["userid"]))
        db.commit()
        cursor.close()
        db.close()
    except:
        e = sys.exc_info()
        with open("error.log", "a") as logfile:
            logfile.write(time.strftime("%d/%m/%Y %H:%M:%S")+" - "+str(e)+"\n")
        db.rollback()
        db.close()
