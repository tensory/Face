#!/usr/bin/env python
#
# process_incoming.py
# by tensory, mct
# not pretty, but we're in a hurry :)
#
# Watches a directory for new jpgs, attempts to match them 
# to a Face.com namespace
 
import sys
import re
import os
import httplib2
import urllib2
import simplejson
import json
import face_client
import time

incoming_dir  = os.path.realpath(os.path.dirname(__file__) + "/incoming")
processed_dir = os.path.realpath(os.path.dirname(__file__) + "/processed")
reversed_html = os.path.realpath(os.path.dirname(__file__) + "/reversed.html")
index_html    = os.path.realpath(os.path.dirname(__file__) + "/index.html")

fbPublicDataBase = 'http://graph.facebook.com/%s?fields=id,link,name,picture&type=large' # *NOT* https

faceApi = {
    'key':'ebfcff03e728bd6d8c60b53d11cc6a7b',
    'password':'27a6b645c50832cc6c537a6852957f97',
    'namespace':'surveillancetruck'
}

http = httplib2.Http()

def extractUserIdByImage(url, client, ns):
    """
    Given an image URL, test it on the face namespace and return the user
    ID of the highest match.  Return False if image not provided or matched
    """
    if (url == False):
        return False
    threshold = 50 # aim for at least 50% match recognition
    recognition = client.faces_recognize('all', url, namespace = ns) # recognition is json
    # Do something with the recognition object
    if recognition:
        topMatch = [recognition['photos'][0]['tags'][0]['uids'][0]]
        if (topMatch[0]['confidence'] >= threshold):
            # grab their ID
            matchObj = re.match(r'(.+[0-9])', topMatch[0]['uid'])
            if len(matchObj.group(0)):
                # Now you have the userID belonging to the FB user.
                return matchObj.group(0)
    return False

def process_one():
    """
    Every second
    capture currentFiles as current return value of os.listdir(path)
    find difference between allFiles and currentFiles
    make API calls to Face on the difference(s)
    all but most recent difference will be overwritten (this is by design
    spit out a new html page
    """

    for file in os.listdir(incoming_dir):
        print "Processing incoming file", file

        # xxx -- upload this file somewhere to somewhere that's publicly accessable
        file_url = 'http://sphotos.xx.fbcdn.net/hphotos-ash3/559477_10100177363179781_22009713_42015310_339035254_n.jpg'

        print "Attempting to recognize face in ", file_url
        userId = extractUserIdByImage(file_url, client, faceApi['namespace'])

        if userId:
            try:
                url = fbPublicDataBase % userId
                print "Found! Reading JSON from URL", url
                content = urllib2.urlopen(url)
                data = json.load(content)

                html = "".join("<tr>",
                    "<td><img src='%s'></td>" % file,
                    "<td><img src='%s'></td>" % data["picture"],
                    "<td><a href='%s'>%s</a></td>" % (data["link"], data["name"]),
                    "</tr>\n")

                print "Done, written out to ", reversed_html
                open(reversed_html, "a").write(html)
            except Exception as e:
                print "Oops, failed:", str(e)
        else:
            print "No match found"
            continue

        lines = open(reversed_html).readlines()
        lines.reverse()
        open(index_html, "w").writelines(lines)

        print "Moving", file, "to", processed_dir
        os.rename(incoming_dir + "/" + file, processed_dir + "/" + file)

if __name__ == '__main__':
    print "Using incoming directory of", incoming_dir
    print "Using processed directory of", processed_dir
    print "Using reversed_html file of", reversed_html
    print "Using index_html file of", index_html
    print
    print "Logging into the face.com API..."
    client = face_client.FaceClient(faceApi['key'], faceApi['password'])
    print "Okay, have the face.com connection handle thingie:", repr(client)
    print

    while True:
        try:
            process_one()
        except Exception as e:
            print "Oops, something died?", str(e)

        print "Sleeping..."
        print
        time.sleep(1)
