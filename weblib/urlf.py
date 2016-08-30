#! /usr/bin/env python

#
# -*- encoding: utf-8 -*-
#

import cgi
import sys
import re
import json
import requests

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

import locale
# Let's set danish locale
locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')


def main(msg=''):
    """All urlf web implementation.

    url forwarder, but drop hidden url
    To use it: import it from
    ../www/urlf or a copy of that folder to the web-server direcotry structure.
    """

    arguments = cgi.FieldStorage()
    u = ''
    if arguments and ('u' in arguments):
        u = arguments['u'].value

    print "Content-type: text/html"
    print "Referer: https://fake.url/" # Not used, but just in case it was used
    # Don't use Location: ..., since this gives client redirect
    print "\n\n" # End of header

    print """<!DOCTYPE html>
  <meta name="referrer" content="no-referrer">
  <html lang="da">
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=%s">
  </html>
""" % u
