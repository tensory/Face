#!/usr/bin/env python
# change to your local Python
#
# checkdir.py
# by tensory 
#
# Watches a directory for new jpgs, attempts to match them 
# to a Face.com namespace
#
# Non-Python dependencies: 
# poster, face_client, httplib2, simplejson
# Install poster from http://pypi.python.org/pypi/poster/0.4
 
import sys, re, os, sched, time, urlparse
import httplib2, simplejson as json
import face_client
import pprint

class Dossier:
    name = "Dossier"
    http = httplib2.Http()
    fbDataBase = 'https://graph.facebook.com/%s?fields=id,link,name,picture&type=large'

    def __init__(self, userId):
        self.userId = userId
        self.link = ''
        self.name = ''
        self.photo = ''
    
    def getDossierData(self):
        response, data = http.request(fbDataBase % self.userId)
        if (data):
            self.link = data['link']
            self.name = data['name']
            self.photo = data['picture']
            return True
        else:
            return False

    def generateFile(self):
        '''
        Generate a new file from the current dossier state.
        '''
        outFile = "index.html"
        path = ""
        inFile = "template.html"
        i = open(inFile, "r")
        o = open(outFile, "w")
        template = i.read()
        '''
        Done reading in the file
        Do string substitution and write it out
        If you change the order of the elements in the template, 
        you must also change it here
        '''
        title = "Transcript #" + self.userId
        custom = template % (title, self.link, self.name, self.photo)
        o.write(custom)
        i.close()
        o.close()
        

def getFriendsUrl(user, token):
    # TODO: This token must be generated.
    # Meantime: get it from http://developers.facebook.com/docs/reference/api/ logged in as mrnightmarket user
    # and then follow instructions at http://itslennysfault.com/get-facebook-access-token-for-graph-api to slurp it up
    # when this thing has a domain.
    base = 'https://graph.facebook.com/%s/friends?access_token=%s&limit=5000&offset=0'
    return base % (user, token)


def extractUserIdByImage(url, client, ns):
    '''
    Given an image URL, test it on the face namespace and return the user ID of the highest match.
    Return 0 if image not provided or matched
    '''
    if (url == False):
        return 0
    threshold = 50 # aim for at least 50% match recognition
    recognition = client.faces_recognize('all', url, namespace = ns)
    # Do something with the recognition object
    if recognition:
        topMatch = [recognition['photos'][0]['tags'][0]['uids'][0]]
        if (topMatch[0]['confidence'] >= threshold):
            # grab their ID
            matchObj = re.match(r'(.+[0-9])', topMatch[0]['uid'])
            if (len(matchObj.group(0))):
                # Now you have the userID belonging to the FB user.
                return matchObj.group(0)
    return 0

    
token = ''
# Needs a valid FB API token
if (len(sys.argv) > 1):
    token = sys.argv[1]
else: 
    print "Need an API token! :("
    sys.exit()

# remove
pp = pprint.PrettyPrinter(indent=4)

path = os.path.realpath(os.path.dirname(__file__) + "/bin")
print "Reading pictures from", path

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
    'password':'27a6b645c50832cc6c537a6852957f97',
    'namespace':'surveillancetruck'
}

# Grab pictures at this URL
fbPublicDataBase = 'https://graph.facebook.com/%s?fields=id,link,name,picture&type=large'

http = httplib2.Http()
# Set up face.com client
client = face_client.FaceClient(faceApi['key'], faceApi['password'])

# Reload the LHNM Facebook user's friend list to keep training the face checker
friendsJsonUrl = getFriendsUrl(fb['username'], token)
result, content = http.request(friendsJsonUrl)
friends = json.loads(content)['data'] # Get just the friends 'data' object from response JSON

# Already ran this. Run again later, but infrequently.
if False:
    # Populate the namespace.
    for friend in friends:
        response, data = http.request(fbPublicDataBase % friend['id'])
        url = json.loads(data)
        # Upload their photo to the Face namespace
        faceResponse = client.faces_detect(url['picture'])
        # Get Face tags
        for photo in faceResponse['photos']:
            if (len(photo['tags']) > 0):
                userTag = [photo['tags'][0]['tid']]
                ns = '%s@%s' % (friend['id'], faceApi['namespace'])
                client.tags_save(tids=userTag, uid=ns, label=friend['name'])
                result = client.faces_train(ns)

# TODO: add user photos as well, see http://developers.facebook.com/docs/reference/api/user/


def loop():
    """
    Every second
    capture currentFiles as current return value of os.listdir(path)
    find difference between allFiles and currentFiles
    make API calls to Face on the difference(s)
    all but most recent difference will be overwritten (this is by design
    spit out a new html page
    """

    currentFiles = os.listdir(path)
    print "Current files:", currentFiles

    kf = set(knownFiles)
    new = [fname for fname in currentFiles if fname not in kf]

    # the 'new' list SHOULD only have one filename in it, as this update should run more slowly than real time 
    #for fname in new:    
    #img = new[0]
    #print img

    # Now try to recognize a given photo
    testPhotoUrl = 'http://sphotos.xx.fbcdn.net/hphotos-ash3/559477_10100177363179781_22009713_42015310_339035254_n.jpg' # Eric M
    userId = extractUserIdByImage(testPhotoUrl, client, faceApi['namespace'])

    if (userId):
        dossier = Dossier(userId)
        if (dossier.getDossierData() == True):
            dossier.generateFile()
        
    # finally, track that these files are done
    knownFiles = currentFiles
    # end stuff to do every second
