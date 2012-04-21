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

if len(sys.argv) < 2:
    print "Usage: %s <id> [id...]" % sys.argv[0]
    sys.exit(0)

training_dir = os.path.realpath(os.path.dirname(__file__) + "/training")

fbPublicDataBase = 'http://graph.facebook.com/%s?fields=id,link,name,picture&type=large' # *NOT* https

print "Using trainining directory of", training_dir

faceApi = {
    'key':'ebfcff03e728bd6d8c60b53d11cc6a7b',
    'password':'27a6b645c50832cc6c537a6852957f97',
    'namespace':'surveillancetruck'
}

http = httplib2.Http()

print "Logging in to face.com"
client = face_client.FaceClient(faceApi['key'], faceApi['password'])

for id in sys.argv[1:]:
    id = int(id)
    print
    print "Contacting Facebook for JSON for", id
    response, data = http.request(fbPublicDataBase % id)
    j = json.loads(data)

    if "id" not in j:
        print "Field 'id' missing?  Skipping"
        continue

    if "picture" not in j:
        print "Field 'picture' missing?  Skipping"
        continue

    print "Sending", j['picture'], "to Face.com"
    faceResponse = client.faces_detect(j['picture'])

    for photo in faceResponse['photos']:
        if len(photo['tags']) > 0:
            userTag = [photo['tags'][0]['tid']]
            tag = '%s@%s' % (id, faceApi['namespace'])
            print "Calling tags_save on", tag
            try:
                client.tags_save(tids=userTag, uid=tag, label=j['id'])
                client.faces_train(tag)
                print "Ok"
            except Exception as e:
                print "Failed:", str(e)
