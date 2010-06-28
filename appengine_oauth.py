#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
AppEngine-OAuth
 
OAuth utility for applications on Google App Engine
 
See: http://0-oo.net/sbox/python-box/appengine-oauth
License: http://0-oo.net/pryn/MIT_license.txt (The MIT license)
'''
 
__author__ = 'dgbadmin@gmail.com'
__version__ = '0.1.0'
 
 
import hmac
import urllib
from google.appengine.api import urlfetch
from hashlib import sha1
from random import getrandbits
from time import time
 
 
class AppEngineOAuth(object):
 
  def __init__(self, key, secret, acs_token='', acs_token_secret=''):
    self._key = key
    self._secret = secret
    self._token = acs_token
    self._token_secret = acs_token_secret
 
    # Be understandable which type token is (request or access)
    if acs_token == '':
      self._token_type = None
    else:
      self._token_type = 'access'
 
 
  def prepare_login(self, req_token_url):
    '''
    Return request_token, request_token_secret and params of authorize url.
    '''
    # Get request token
    params = self.get_oauth_params(req_token_url, {})
    res = urlfetch.fetch(url=req_token_url + '?' + urllib.urlencode(params),
                         method='GET')
    self.last_response = res
    if res.status_code != 200:
      raise Exception('OAuth Request Token Error: ' + res.content)
    # Response content is request_token
    dic = self._qs2dict(res.content)
    self._token = dic['oauth_token']
    self._token_secret = dic['oauth_token_secret']
    self._token_type = 'request'
 
    # Get params with signature
    sig_params = {'oauth_signature': params['oauth_signature']}
    dic['params'] = urllib.urlencode(self.get_oauth_params(req_token_url,
                                                           sig_params))
 
    return dic
 
 
  def exchange_tokens(self, acs_token_url, req_token, req_token_secret):
    self._token = req_token
    self._token_secret = req_token_secret
    self._token_type = 'request'
 
    params = urllib.urlencode(self.get_oauth_params(acs_token_url, {}))
    res = urlfetch.fetch(url=acs_token_url, payload=params, method='POST')
    self.last_response = res
    if res.status_code != 200:
      raise Exception('OAuth Access Token Error: ' + res.content)
    # Response content is access_token
    dic = self._qs2dict(res.content)
    self._token = dic['oauth_token']
    self._token_secret = dic['oauth_token_secret']
    self._token_type = 'access'
 
    return dic
 
 
  def get_oauth_params(self, url, params, method='GET'):
    oauth_params = {'oauth_consumer_key': self._key,
                    'oauth_signature_method': 'HMAC-SHA1',
                    'oauth_timestamp': int(time()),
                    'oauth_nonce': getrandbits(64),
                    'oauth_version': '1.0'}
    if self._token_type != None:
      oauth_params['oauth_token'] = self._token
 
    # Add other params
    params.update(oauth_params)
 
    # Sort and concat
    s = ''
    for k in sorted(params):
      s += self._quote(k) + '=' + self._quote(params[k]) + '&'
    msg = method + '&' + self._quote(url) + '&' + self._quote(s[:-1])
 
    # Maybe token_secret is empty
    key = self._secret + '&' + self._token_secret
 
    digest = hmac.new(key, msg, sha1).digest()
    params['oauth_signature'] = digest.encode('base64')[:-1]
 
    return params
 
 
  def _quote(self, s):
    return urllib.quote(str(s), '')
 
 
  def _qs2dict(self, s):
    dic = {}  
    for param in s.split('&'):
      (key, value) = param.split('=')
      dic[key] = value
    return dic
