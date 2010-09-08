#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from appengine_twitter import AppEngineTwitter
from basehandler import BaseHandler, h
import twitter
import sys, os, pickle
from oauthtwitter import *

# User Setting and Run Twitter Bot
#debug_flag = True
debug_flag = False
MAX_LEN = 140
SEARCH_TERM = u'"Cafe Miyama" OR カフェミヤマ'
CONSUMER_KEY    = "???"
CONSUMER_SECRET = "???"
KEY_FILE_API    = "api_key.dat"
KEY_FILE_TWITTER = "twitter_key.dat"
BOT_USERNAME = "CafeMiyamaBot"
BOT_PASSWORD = "???"

def oauth_twitter():
   access_token = pickle.load(file(KEY_FILE_API))
   return OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
                                                                      
# twitter.Api.__init__ method for override.
def twitter_api_init_gae(self,
                       username=None,
                       password=None,
                       input_encoding=None,
                       request_headers=None):
   import urllib2
   from twitter import Api
   self._cache = None

   self._urllib = urllib2
   self._cache_timeout = Api.DEFAULT_CACHE_TIMEOUT
   self._InitializeRequestHeaders(request_headers)
   self._InitializeUserAgent()
   self._InitializeDefaultParameters()
   self._input_encoding = input_encoding
   self.SetCredentials(username, password)

def run(name, pswd, search_term):
   acc_token = pickle.load(file(KEY_FILE_API))
   gae_twitter = AppEngineTwitter()   
   gae_twitter.set_oauth(CONSUMER_KEY,
                         CONSUMER_SECRET,
                         acc_token.key,
                         acc_token.secret)

   results = gae_twitter.search(search_term.encode('utf8'), {'rpp': 20})
   api = oauth_twitter() #twitter.Api(username=bot_username, password=bot_password)
   escape_user_list = []
   escape_user_list.append(name)
   
   # Get most corrently tweeted tweet
   status = api.GetUserTimeline()

   if debug_flag:
      print "Debugging..."
      hoge = api.GetReplies()
      for h in hoge:
         print h
   
   for s in status:
      if s.text.startswith("RT"):
         recent_tweet = s.text
         break
      else:
         print "The following tweet would be posted by hand, so skipped it."
         print "Tweet: " + s.text.encode('utf8')
         print
      
   print "Recent Tweet: "+recent_tweet.encode('utf8')
   print

   # Search Most Recent Tweet
   results.reverse()
   flag_enable = 0
   for i,result in enumerate(results):
      rt = "RT [at]" + result['from_user']  + " " + result['text']
      rt_len = len(rt)
      if debug_flag:
         print "[Debug] rt["+str(i)+"]: " + rt.encode('utf8') 
      
      if flag_enable:
         print "I am going to tweet the tweet above."
         if rt_len > MAX_LEN:
            print "But, this tweet length is longer that 140 characters, so skipped it."
            continue
         if result['from_user'] in escape_user_list:
            print "But, this tweet above is tweeted by Escape User, so skipped it."
            continue
         if result['text'].startswith('@'):
            print "But, this tweet above starts with '@', so skipped it."
            continue
         """
         Retweet and exit
         """
         if debug_flag:
            print "Next Tweet: "+rt.encode('utf8')
         else:
            print "I have re-tweeted: "+rt.encode('utf8')
            print "Result of my re-tweeting: " + str(gae_twitter.update(rt.encode('utf8')))
         exit()
               
      if recent_tweet.replace("@", "[at]") == rt.replace("@", "[at]"):
         if debug_flag:
            print "My Most Recent Tweet: " + recent_tweet.encode('utf8')
            print "-----------------------------------------------------"
         flag_enable = 1

   if flag_enable:
      print "There are no tweet found that I should tweet."
      exit()
   print
   print "There are no tweets recently tweeted, so tweet the oldest tweet."
   print
#   print "results: ",
#   print str(results)
   for i,result in enumerate(results):  
      rt = "RT [at]" + result['from_user']  + " " + result['text']  
      rt_len = len(rt)
      if debug_flag:
         print "[Debug] rt["+str(i)+"]: " + rt.encode('utf8') 

      print "I am going to tweet the tweet above."
      if rt_len > MAX_LEN:
         print "But, this tweet length is longer that 140 characters, so skipped it."
         continue
      if result['from_user'] in escape_user_list:
         print "But, this tweet above is tweeted by Escape User, so skipped it."
         continue
      if result['text'].startswith('@'):
         print "But, this tweet above starts with '@', so skipped it."
         continue
      """
      Retweet and exit
      """
      if debug_flag:
         print "Next Tweet: "+rt.encode('utf8')
      else:
         print "I have tweeted: "+rt.encode('utf8')
         print "Result of my re-tweeting: " + str(gae_twitter.update(rt.encode('utf8')))
      exit()

# overriding API __init__
twitter.Api.__init__ = twitter_api_init_gae

# Start to run
run(BOT_USERNAME, BOT_PASSWORD, SEARCH_TERM)
