#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
AppEngine-Twitter
 
Twitter API wrapper for applications on Google App Engine
 
See: http://0-oo.net/sbox/python-box/appengine-twitter
License: http://0-oo.net/pryn/MIT_license.txt (The MIT license)
 
See also:
  http://apiwiki.twitter.com/Twitter-API-Documentation
  http://code.google.com/intl/ja/appengine/docs/python/urlfetch/
'''
 
__author__ = 'dgbadmin@gmail.com'
__version__ = '0.1.0'
 
 
import base64
import urllib
from appengine_oauth import AppEngineOAuth
from django.utils import simplejson
from google.appengine.api import urlfetch
 
 
class AppEngineTwitter(object):
 
  def __init__(self, tw_name='', tw_pswd=''):
    '''
    Note: Some actions require password or OAuth.
    '''
    self._api_url = 'https://twitter.com'
    self._search_url = 'http://search.twitter.com'
 
    self.tw_name = tw_name
    self._oauth = None
 
    self._headers = {}
    if tw_pswd != '':
      auth = base64.encodestring(tw_name + ':' + tw_pswd)[:-1]
      self._headers['Authorization'] = 'Basic ' + auth
 
 
  def update(self, message):
    '''
    Post a tweet
    Sucess => Retrun 200 / Fialed => Return other HTTP status
    '''
    return self._post('/statuses/update.json', {'status': message})
 
 
  def follow(self, target_name):
    '''
    Sucess => Return 200 / Already following => Return 403 /
    Fialed => Return other HTTP status
    '''
    return self._post('/friendships/create.json', {'screen_name': target_name})
 
 
  def is_following(self, target_name):
    '''
    Yes => Return True / No => Return False /
    Fialed => Return HTTP status except 200
    '''
    if self.tw_name == '':
      # With OAuth, screen_name is not required.
      self.verify()
      user_info = simplejson.loads(self.last_response.content)
      self.tw_name = user_info['screen_name']
 
    status = self._get('/friendships/exists.json',
                       {'user_a': self.tw_name, 'user_b': target_name})
    if status == 200:
      return (self.last_response.content == 'true')
    else:
      return status
 
 
  def verify(self):
    '''
    Verify user_name and password, and get user info
    Sucess => Return 200 / Fialed => Return other HTTP status
    '''
    return self._get('/account/verify_credentials.json', {})
 
 
  def search(self, keyword, params={}):
    '''
    Sucess => Return Array of dict / Fialed => Return HTTP status except 200
    '''
    params['q'] = keyword
    return self._search('/search.json', params)
 
 
  # OAuth methods
  # (See http://0-oo.net/sbox/python-box/appengine-oauth )
 
  def set_oauth(self, key, secret, acs_token='', acs_token_secret=''):
    '''
    Set OAuth parameters
    '''
    self._oauth = AppEngineOAuth(key, secret, acs_token, acs_token_secret)
 
 
  def prepare_oauth_login(self):
    '''
    Get request token, request token secret and login URL
    '''
    dic = self._oauth.prepare_login(self._api_url + '/oauth/request_token/')
    dic['url'] = self._api_url + '/oauth/authorize?' + dic['params']
    return dic
 
 
  def exchange_oauth_tokens(self, req_token, req_token_secret):
    '''
    Exchange request token for access token
    '''
    return self._oauth.exchange_tokens(self._api_url + '/oauth/access_token/',
                                       req_token,
                                       req_token_secret)
 
 
  # Private methods
 
  def _post(self, path, params):
    url = self._api_url + path
    if self._oauth != None:
      params = self._oauth.get_oauth_params(url, params, 'POST')
    res = urlfetch.fetch(url=url,
                         payload=urllib.urlencode(params),
                         method='POST',
                         headers=self._headers)
    self.last_response = res
    return res.status_code
 
 
  def _get(self, path, params):
    url = self._api_url + path
    if self._oauth != None:
      params = self._oauth.get_oauth_params(url, params, 'GET')
    url += '?' + urllib.urlencode(params)
    res = urlfetch.fetch(url=url, method='GET', headers=self._headers)
    self.last_response = res
    return res.status_code
 
 
  def _search(self, path, params):
    '''
    FYI http://apiwiki.twitter.com/Rate-limiting (Especially 503 error)
    '''
    url = url=self._search_url + path + '?' + urllib.urlencode(params)
    res = urlfetch.fetch(url=url, method='GET')
    self.last_response = res
 
    if res.status_code == 200:
      return simplejson.loads(res.content)['results']
    elif res.status_code == 503:
      err_msg = 'Rate Limiting: Retry After ' + res.headers['Retry-After']
    else:
      err_msg = 'Error: HTTP Status is ' + str(res.status_code)
 
    raise Exception('Twitter Search API ' + err_msg)
