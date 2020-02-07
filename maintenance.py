#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
import os
import random
from texts import *

from flask import Flask
from flask import request
from flask import make_response

__author__ = "Dominik Fehr"
__copyright__ = "Copyright 2017 "+__author__
__credits__ = ""
__license__ = "Internal"
__version__ = "05.04.2017"
__maintainer__ = "Dominik Fehr"
__email__ = "df@legit-it.de"
__status__ = "Development"

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/mbot', methods=['POST'])
def webhook():
    #check auth
    if(request.headers['token']!='apiai'):
        res = {
            "speech":"ERROR t0ken not where it should be!",
            "source":"Tunes2u"
        }
        res = json.dumps(res, indent=4)
        r = make_response(res)
        r.hreaders['Content-Type'] = 'application/json'
        return r

    req = request.get_json(silent=True, force=True)
    res = makeWebhookResult(req, req.get('lang'))
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req, lang):
    if("de" in lang.lower()):
        speech = random.choice(MAINTENANCE_1_DE)
    else:
        speech = random.choice(MAINTENANCE_1_EN)

    return {
        "speech": speech,
        "displayText": speech,
        "source": "Tunes2u"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print ("Starting Tunes2u maintenance mode on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
