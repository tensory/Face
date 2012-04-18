# #!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

# checkdir.py
# by tensory 
#
# Watches a directory for new files, 
# does a thing when they're ready
#
# Non-Python dependencies: 
# poster, face_client, httplib2, simplejson
# Install poster from http://pypi.python.org/pypi/poster/0.4
 
import os, sched, time, urlparse
import httplib2, simplejson as json
import face_client
import pprint # not required, get rid of later

# Get the app access token from Facebook 
def getAppAccessToken(app_id, secret):
    url = 'https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials' % (app_id, secret)
    response, content = httplib2.Http().request(url)
    return content

def getUserAccessToken(app_id, redirect, state, http):
    scopes = ['friends_photos', 'friends_photo_video_tags', 'offline_access']
    url = 'https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&scope=%s&state=%s'
    url = url % (app_id, redirect, ','.join(scopes), state)
    print http.request(url)
    return ''

def getFriendsUrl(user):
    # TODO: This token must be generated.
    # Meantime: get it from http://developers.facebook.com/docs/reference/api/ logged in as mrnightmarket user
    # and then follow instructions at http://itslennysfault.com/get-facebook-access-token-for-graph-api to slurp it up
    # when this thing has a domain.
    token = 'AAAAAAITEghMBAP53uwyNmbd997sKimHsZBdTLTPQJG2c9I6zDsgXuLrTJgkIm30aos9LLbU8IvHXiZCZA0LAZB65zLKxPCKiWG3XK6pZBR6ZCGHAlztFmj'
    base = 'https://graph.facebook.com/%s/friends?access_token=%s&limit=5000&offset=0'
    return base % (user, token)

# remove
pp = pprint.PrettyPrinter(indent=4)

path = '/Users/alacenski/Documents/Projects/Face/bin' # TODO: change this to run in the current directory
knownFiles = []
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
faceApi = {
    'key':'ebfcff03e728bd6d8c60b53d11cc6a7b',
    'password':'27a6b645c50832cc6c537a6852957f97'
}

http = httplib2.Http()
# Set up face.com client
faceClient = face_client.FaceClient(faceApi['key'], faceApi['password'])

# Get API access token
state = 'foo'
token = getUserAccessToken(fbApi['app_id'], fb['domain'], state, http)

# Reload the LHNM Facebook user's friend list to keep training the face checker
#friendsJsonUrl = getFriendsUrl(fb['username'])
#result, content = http.request(friendsJsonUrl)
#friends = json.loads(content)['data'] # Get just the friends 'data' object from response JSON
#pp.pprint(friends) # yay


# start downloading people's usericons
#for friend in friends:
#    fData = json.loads(friend)
#    print friend['id']

# Every second
# capture currentFiles as current return value of os.listdir(path)
# find difference between allFiles and currentFiles
# make API calls to Face on the difference(s)
# all but most recent difference will be overwritten (this is by design
# spit out a new html page

# do this every second:
currentFiles = os.listdir(path)
kf = set(knownFiles)
new = [fname for fname in currentFiles if fname not in kf]

# the 'new' list SHOULD only have one filename in it, as this update should run more slowly than real time 
#for fname in new:
    
#img = new[0]
#print img

# finally, track that these files are done
knownFiles = currentFiles
# end stuff to do every second
