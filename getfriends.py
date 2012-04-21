#!/usr/bin/env python
# getfriends.py
# by tensory
#
# get friend IDs of friends of mrnightmarket

import sys, os
import simplejson, httplib2
import pprint

def getFriendsUrl(user, token):
    base = 'https://graph.facebook.com/%s/friends?access_token=%s&limit=5000&offset=0'
    return base % (user, token)

token = ''
user = 'mrnightmarket'
fb_public_query = 'https://graph.facebook.com/%s?fields=id,picture&type=large'
http = httplib2.Http()
pp = pprint.PrettyPrinter(indent=4)
outfile = "friends_of_mrnightmarket.txt"

if (len(sys.argv) > 1):
    token = sys.argv[1]
else: 
    print "Need an API token! :("
    sys.exit()
    
friends_json_url = getFriendsUrl(user, token)
result, content = http.request(friends_json_url)
friends = simplejson.loads(content)['data'] # Get just the friends 'data' object from response JSON

if os.path.isfile(outfile):
	os.remove(outfile) # Get rid of old copies

handle = open(outfile, "w")

for friend in friends:
	if not friend['id']:
		continue
	handle.writelines(friend['id'] + '\n')

print "Done"
handle.close()