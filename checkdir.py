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
 
import sys, os, sched, time, urlparse
import httplib2, simplejson as json
import face_client
import pprint # not required, get rid of later


def getFriendsUrl(user, token):
    # TODO: This token must be generated.
    # Meantime: get it from http://developers.facebook.com/docs/reference/api/ logged in as mrnightmarket user
    # and then follow instructions at http://itslennysfault.com/get-facebook-access-token-for-graph-api to slurp it up
    # when this thing has a domain.
    base = 'https://graph.facebook.com/%s/friends?access_token=%s&limit=5000&offset=0'
    return base % (user, token)

token = ''
# Needs a valid FB API token
if (len(sys.argv) > 1):
    token = sys.argv[1]
else: 
    print "Need an API token! :("
    sys.exit()

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
    'secret':'78fe31e68c7f856cd95f4e42a209c222',
    'token': token
}

faceApi = {
    'key':'ebfcff03e728bd6d8c60b53d11cc6a7b',
    'password':'27a6b645c50832cc6c537a6852957f97'
}

# Grab pictures at this URL
fbPublicDataBase = 'https://graph.facebook.com/%s?fields=picture&type=large'

http = httplib2.Http()
# Set up face.com client
client = face_client.FaceClient(faceApi['key'], faceApi['password'])

# Reload the LHNM Facebook user's friend list to keep training the face checker
friendsJsonUrl = getFriendsUrl(fb['username'], token)
result, content = http.request(friendsJsonUrl)
friends = json.loads(content)['data'] # Get just the friends 'data' object from response JSON
#pp.pprint(friends) # yay

for friend in friends:
    response, data = http.request(fbPublicDataBase % friend['id'])
    url = json.loads(data)
    # Upload their photo to the Face namespace
    faceResponse = client.faces_detect(url['picture'])
    # Get Face tags
    for photo in faceResponse['photos']:
        #print photo
        if (len(photo['tags']) > 0):
            print [photo['tags'][0]['tid']]


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
