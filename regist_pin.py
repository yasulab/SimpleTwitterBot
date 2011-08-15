#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, pickle
from oauthtwitter import *

KEY_FILE_API    = "api_key.dat"

def twitter():
    if os.path.isfile(KEY_FILE_API):
        CONSUMER_KEY = raw_input("What is your CONSUMER_KEY? ")
        CONSUMER_SECRET = raw_input("What is your CONSUMER_SECRET? ")
        access_token = pickle.load(file(KEY_FILE_API))
    else:
        CONSUMER_KEY = raw_input("What is your CONSUMER_KEY? ")
        CONSUMER_SECRET = raw_input("What is your CONSUMER_SECRET? ")
        tw = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET)
        request_token = tw.getRequestToken()
        authorization_url = tw.getAuthorizationURL(request_token)
        print "Please visit the following URL with your web browser."
        print authorization_url
        print
        print "If you did your registration correctly, you can see some numbers"
        print "(If not, maybe you had not chosen client type during Twitter OAuth registration)"
        print 
        tw = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, request_token)
        oauth_verifier = raw_input("What is the number(PIN)? ")
        access_token = tw.getAccessTokenWithPin(oauth_verifier)
        print "Finished setting OAuth configuration."
        print "Now, you can use OAuth. Enjoy!"
    
    pickle.dump(access_token, file(KEY_FILE_API, "w"))
    return OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)

def main(args):
    tw = twitter()
    if len(args) < 2:
        for status in tw.GetFriendsTimeline(count=20):
            print status.GetUser().GetScreenName() + ":", status.GetText().encode("cp932", "replace")
    else:
        post = " ".join(args[1:])
        tw.PostUpdate(post.decode("cp932").encode("utf-8"))

if __name__ == "__main__": main(sys.argv)
