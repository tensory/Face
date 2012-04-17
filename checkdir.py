#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python

# checkdir.py
# by tensory 
#
# Watches a directory for new files, 
# does a thing when they're ready
#
# Non-Python dependencies: 
# poster, face_client, httplib2, simplejson
# Install poster from http://pypi.python.org/pypi/poster/0.4
 
import os, simplejson, httplib2, sched, time
import face_client

# Get the app access token from Facebook 
def getFacebookAccessToken(app_id, secret):
    url = 'https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials' % (app_id, secret)
    response, content = httplib2.Http().request(url)
    return content


def getFriendsUrl(user):
    token = 'AAAAAAITEghMBAJgkxeziB6WzqgBQDHJ6OXNWx6VCw7Ic6TTZCp2MszNY9wir9cZAN6xKPxRFDeQgm3hmJCLwMBEe7AbwqWnN6Af0sEfGnmkrd9zZAER'
    base = 'https://graph.facebook.com/%s/friends?access_token=%s&limit=5000&offset=0'
    return base % (user, token)

path = '/Users/alacenski/Documents/Projects/Face/bin' # change this to run in the current directory
knownFiles = []
fb = {
    'login':'mrnightmarket@stupidthing.org',
    'password':'QZ2YHcwHfi2DBJSPJNhE',
    'username':'mrnightmarket'
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
friendsJsonUrl = getFriendsUrl(fb['username'])
result = http.request(friendsJsonUrl)

# stuck here, trying to load json result into a python obj
friendsJson = simplejson.load(result[1]);


# Reload the LHNM Facebook user's friend list to keep training the face checker

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
    
img = new[0]
print img

# finally, track that these files are done
knownFiles = currentFiles
# end stuff to do every second
