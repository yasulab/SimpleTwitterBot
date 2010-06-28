#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
AppEngine-BaseHandler
 
A little useful RequestHandler on Google App Engine,
and some common functions.
 
See: http://0-oo.net/sbox/python-box/appengine-basehandler
License: http://0-oo.net/pryn/MIT_license.txt (The MIT license)
'''
 
__author__ = 'dgbadmin@gmail.com'
__version__ = '0.1.0'
 
import xml.sax.saxutils
from google.appengine.ext import webapp
 
 
class BaseHandler(webapp.RequestHandler):
 
  def p(self, out, brFlg=False):
    '''
    write out, with BR tag if you want
    '''
    self.response.out.write(out)
    if brFlg == True:
      self.response.out.write('<br />')
    self.response.out.write('\n')
 
 
  def simple_header(self, title, option=''):
    '''
    Minimum HTML header
    '''
    self.p('<html>')
    self.p('<head>')
    self.p('<title>' + h(title) + '</title>')
    self.p(option)
    self.p('</head>')
    self.p('<body>')
 
 
  def simple_footer(self):
    '''
    Minimum HTML footer
    '''
    self.p('</body>')
    self.p('</html>')
 
 
 
# Common functions
 
def h(out):
  '''
  HTML escape
  '''
  return xml.sax.saxutils.escape(out, {'"': "&quot;"})
 
 
def sort_dict(dic, by='key', reverse=False):
  '''
  Note: This function returns tuple 
  '''
  if by == 'key':
    i = 0
  elif by == 'value':
    i = 1
  else:
    raise Exception('Unexpected "by"')
 
  return sorted(dic.items(), lambda x,y : cmp(x[i], y[i]), reverse=reverse)
