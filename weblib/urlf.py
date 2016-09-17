# -*- coding: utf-8 -*-

import cgi
import sys
import re
import json
import requests
import os

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
  <script type="text/javascript">
    window.location = "%s";
  </script>
  <title>Link til %s</title>
  <body>
    <h2>Link til <a href="%s">%s</a></h2>

    <h3>Hvorfor ser jeg denne side?</h3>
    <p>Grunden til at du ser denne side, og ikke kommer videre er at din browser er sat til at ignorere %s.
    <a href="%s">Søg på google for at slå det til i din browser</a>.
    <br>
    Desuden er javascript sandsynligvis også slået fra, ellers bude det også have sendt dig videre.
    </p>
  <body>
  </html>
""" % (u, u, u, u, u,
       cgi.escape('<meta http-equiv="refresh">'),
       cgi.escape('https://www.google.dk/search?q=<meta http-equiv=refresh>+does+not+work+' + os.environ["HTTP_USER_AGENT"] + '"'),
)
