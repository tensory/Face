#!/usr/bin/env python

# runfirst.py
# by tensory

'''
Facebook won't let you run random queries against the graph api
without an access token

so, run this script BEFORE attempting to run checkdir.py
and feed the resulting token to checkdir.py

sucks, I know

Non-Python dependencies: 
httplib2
'''

import urlparse, httplib2
fb = { 
    'login':'mrnightmarket@stupidthing.org',
    'password':'QZ2YHcwHfi2DBJSPJNhE',
    'username':'mrnightmarket',
    'domain':'http://www.stupidthing.org'
}

fbApi = {
    'app_id':'199009273549135',
    'secret':'78fe31e68c7f856cd95f4e42a209c222'
}

def getUserAccessToken(app_id, redirect, state, http):
    scopes = ['user_photo_video_tags', 'friends_photo_video_tags', 'offline_access']
    url = 'https://www.facebook.com/dialog/oauth?type=user_agent&client_id=%s&redirect_uri=%s&scope=%s&state=%s'
    return url % (app_id, redirect, ','.join(scopes), state)

http = httplib2.Http()
state = 'irrelevant' # really, since we're not checking it like responsible grownups

print "Requesting Facebook access token for mrnightmarket..."
print "Copy and paste this URL in a browser to get your token.\n"
print getUserAccessToken(fbApi['app_id'], fb['domain'], state, http)
print '\nNow copy the access_token part of the URL you are redirected to ONLY, not the code= or expires_in= or any other bits.'
