#!/usr/bin/env python
#
# train.py
# by tensory, mct
#
# Reads a list of facebook IDs from command line arguments, queries Facebook
# for their profile picture, copied the picture to a local directory, and then
# attempts to contact face.com to add it to our training corpus.
#
# not pretty, but we're in a hurry :)
 
import sys
import urllib
import json
import face_client
import pprint
pp = pprint.PrettyPrinter(indent=4)

if len(sys.argv) < 2:
    print "Usage: %s <id> [id...]" % sys.argv[0]
    sys.exit(0)

fbPublicDataBase = 'http://graph.facebook.com/%s?fields=id,link,name,picture&type=large' # *NOT* https

faceApi = {
    'key':'ebfcff03e728bd6d8c60b53d11cc6a7b',
    'password':'27a6b645c50832cc6c537a6852957f97',
    'namespace':'nighttest'
}

print "Populating namespace", faceApi['namespace']

print "Logging in to face.com"
face_client.set_log_level(9)
client = face_client.FaceClient(faceApi['key'], faceApi['password'], ssl=False)

counter_ok = 0
counter_no_id = 0
counter_no_face = 0
counter_low_confidence = 0
counter_face_fail = 0

for id in sys.argv[1:]:
    print
    print "Contacting Facebook for JSON for", id
    content = urllib.urlopen(fbPublicDataBase % id).read()
    j = json.loads(content)

    if "id" not in j:
        print "Field 'id' missing?  Skipping"
        counter_no_id += 1
        continue

    print "Facebook ID is", j['id']

    if "picture" not in j:
        print "Field 'picture' missing?  Skipping"
        counter_no_id += 1
        continue

    print "Fetching", j['picture']
    imagedata = urllib.urlopen(j['picture']).read()

    localfile = "profilepictures/%s.jpg" % j['id']
    print "Writing to", localfile
    open(localfile, "w").write(imagedata)

    print "Calling API faces_detect"
    face_response = client.faces_detect(file_name=localfile)

    if not face_response['photos']:
        print "No photos?"
        continue

    #pp.pprint(face_response)

    for photo in face_response['photos']:
        if not photo['tags']:
            print "No tags found"
            counter_no_face += 1
            continue

        confidence = photo['tags'][0]['attributes']['face']['confidence']
        print "Face confidence", confidence
        if confidence < 60:
            print "Skipping low confidence"
            counter_low_confidence += 1
            continue

        # TID is the temporary ID for the face that face.com detected in the photo
        # We now want to associate it with a UID we define, which will be returned if we recognize this person later
        tid = photo['tags'][0]['tid']
        uid = '%s@%s' % (j['id'], faceApi['namespace'])

        try:
            print "Calling tags_save on", uid
            client.tags_save(tids=tid, uid=uid)

            print "Calling faces_train on", uid
            client.faces_train(uid)

            print "Ok"
            counter_ok += 1

        except Exception as e:
            print "Failed:", str(e)
            counter_face_fail += 1
            sys.exit()


print
print "OK", counter_ok
print "No ID", counter_no_id
print "No Face", counter_no_face
print "Low confidence", counter_low_confidence
print "Face fail", counter_face_fail
