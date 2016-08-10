#! /usr/bin/env python

#
# -*- encoding: utf-8 -*-
#

import sqlite3
import datetime
import cgi
import sys
import re
import json

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

import locale
# Let's set danish locale
locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')

def connectDb(db):
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)
    return conn, c

def getClasses(dbc):
    dbc.execute('SELECT * FROM classes order by class')
    classes = {}
    for id, kl in dbc.fetchall():
        classes[id] = kl
    return classes

def getLektier(dbc, lektieIDs, predays = 1, days = 30):
    """Return list of lektier for the classes with lektieIDs for the comming days

    predays: How many days before tomorrow 0=from tomorrow, 1=from today, 2=from yesterday, ...
    Format:
    list with entry for each of the days no matter if there are lektier or not.
    For each day there is a dict with:
    - day: Type: datetime.date
    - hit: Entries found for today for any of the IDs Type: boolean
    - lektier: dict: lektier[id].
         lektier[id] is a list with an list for each fag containg:
         - fag-name
         - What to do
         - When it was seen first time
         - When it was updated (if no update None)
    """
    
    data = []

    for delta_days in xrange(-predays, days):
        # Day, +1 since tomorrow is reference
        day = datetime.date.today() + datetime.timedelta(days=delta_days +1)
        # Select lektier for day
        entries_found_for_day = False # Any lektier for day?
        lektie = {}
        for id in lektieIDs:
            d = (id, day,)
            dbc.execute('SELECT fag, lektie, created, updated FROM lektier where id=? and day=?', d)
            lektie[id] = dbc.fetchall()
            if lektie[id]:
                entries_found_for_day = True
        data.append({'delta': delta_days, 'day': day, 'lektie': lektie, 'hit': entries_found_for_day})
    return data

def main(db):
    """All lektie web implementation.

    To use it either use this file directly or import it from
    ../www/lektier or a copy of that folder to the web-server direcotry structure.
    """

    print "Content-type: text/html\n\n"
    print """<html>
  <head>
    <meta charset="UTF-8">
    <title>LektieWeb</title>

    <link rel="apple-touch-icon" sizes="57x57" href="/fskintra/favicons/apple-touch-icon-57x57.png?v=1.1.0">
    <link rel="apple-touch-icon" sizes="60x60" href="/fskintra/favicons/apple-touch-icon-60x60.png?v=1.1.0">
    <link rel="apple-touch-icon" sizes="72x72" href="/fskintra/favicons/apple-touch-icon-72x72.png?v=1.1.0">
    <link rel="apple-touch-icon" sizes="76x76" href="/fskintra/favicons/apple-touch-icon-76x76.png?v=1.1.0">
    <link rel="apple-touch-icon" sizes="114x114" href="/fskintra/favicons/apple-touch-icon-114x114.png?v=1.1.0">
    <link rel="apple-touch-icon" sizes="120x120" href="/fskintra/favicons/apple-touch-icon-120x120.png?v=1.1.0">
    <link rel="apple-touch-icon" sizes="144x144" href="/fskintra/favicons/apple-touch-icon-144x144.png?v=1.1.0">
    <link rel="apple-touch-icon" sizes="152x152" href="/fskintra/favicons/apple-touch-icon-152x152.png?v=1.1.0">
    <link rel="apple-touch-icon" sizes="180x180" href="/fskintra/favicons/apple-touch-icon-180x180.png?v=1.1.0">
    <link rel="icon" type="image/png" href="/fskintra/favicons/favicon-32x32.png?v=1.1.0" sizes="32x32">
    <link rel="icon" type="image/png" href="/fskintra/favicons/android-chrome-192x192.png?v=1.1.0" sizes="192x192">
    <link rel="icon" type="image/png" href="/fskintra/favicons/favicon-96x96.png?v=1.1.0" sizes="96x96">
    <link rel="icon" type="image/png" href="/fskintra/favicons/favicon-16x16.png?v=1.1.0" sizes="16x16">
    <link rel="manifest" href="/fskintra/favicons/manifest.json?v=1.1.0">
    <link rel="mask-icon" href="/fskintra/favicons/safari-pinned-tab.svg?v=1.1.0" color="#5b71d5">
    <link rel="shortcut icon" href="/fskintra/favicons/favicon.ico?v=1.1.0">
    <meta name="msapplication-TileColor" content="#da532c">
    <meta name="msapplication-TileImage" content="/fskintra/favicons/mstile-144x144.png?v=1.1.0">
    <meta name="msapplication-config" content="/fskintra/favicons/browserconfig.xml?v=1.1.0">
    <meta name="theme-color" content="#505050">

    <style>
     .oldday, .today, .nextday, .day, .kl {
       font-weight: bold;
       font-size: large;
     }
     .oldday {
       color: rgb(100,100,100);
     }
     .today {
       color: rgb(155,50,50);
     }
     .nextday {
       color: rgb(255,50,50);
     }
     .day {
       color: rgb(0,0,200);
     }
     .fag {
     }
     .do {
     }
     .seen {
       font-size: small;
       color: rgb(128,128,128);
     }
     li {
       margin: 0;
       padding: 0.0em;
     }
    </style>
  </head>
  <body>
"""

    dbconn, dbc = connectDb(db)

    arguments = cgi.FieldStorage()
    if not arguments:
        print """    <h1>Ops&aelig;tning</h1>
    <p>
      Ops&aelig;tning af web lektie overblik.
      <br>
      V&aelig;lg hvilke klasser du &oslash;nsker at se lektier for, og hvor mange dage frem.
      Tryk p&aring; Videre.
    </p>
    <p>
      Du kan bookmarke den side som du kommer til, og du vil fremover se lektier for de valgte klasser for det valgte antal dage.
      <br>
      Du kan ogs&aring; gemme den p&aring; startsk&aelig;rmen af en smartphone (som en app), hvis du i browserens menu v&aelig;lger "F&oslash;j til startsk&aelig;rm" eller lignende.
    </p>
"""

        print '<p><form method="GET" action="?a=1">'
        for i in xrange(5):  # Max 5 klasser
            print "%d. valg: <select name=kl%d>" % (i+1, i)
            print '<option value="-">-</option>'
            dbc.execute('SELECT * FROM classes order by class')
            classes = {}
            for id, kl in dbc.fetchall():
                print '<option value="%s">%s</option>' % (id, kl)
            print '</select></br>'
        print '</p>'
        print '<p>'
        print 'Antal dage bagud: <select name=predays>'
        for i in range(0,8):
            print '<option',
            if i == 1:  # Selected
                print ' selected',
            print ' value="%d">%d</option>' % (i, i)
        print '</select> (0=Fra i morgen, 1 fra i dag, ...)</br>'
        print '</p>'
        print '<p>'
        print 'Antal dage fremad:<select name=days>'
        for i in range(1,30+1):
            print '<option',
            if i == 30:  # Selected
                print ' selected',
            print ' value="%d">%d</option>' % (i, i)
        print "</select></br>"
        print '</p>'
        print '<p>'
        print '<input type="submit" value="Ok">'
        print '</form></p>'
        print '</body>'
        print '</html>'
    else:  # Arguments given, show data
        classes = getClasses(dbc)
        # Get which lektieIDs to show, either via kl=all, kl=[id1, id2, ...] or kl0=id0, kl1=id1, .., kl4=id4
        lektieIDs = [];
        if 'kl' in arguments:
            if arguments['kl'].value == 'all':
                lektieIDs = sorted(classes, key=classes.get)
            elif re.match('^\s*\[([0-9]+,\s*)*[0-9]+\]\s*$', arguments['kl'].value):
                # Shall be on list form [num, num, num]
                lektieIDs = []
                for idInt in json.loads(arguments['kl'].value):
                    if idInt in classes:
                        lektieIDs.append(idInt)
        else:
            # Sanitize arguments kl0-kl4 which classes to show for, store relevant data in lektieIDs
            for kl in ['kl0', 'kl1', 'kl2', 'kl3', 'kl4']:
                try:
                    idInt = int(arguments[kl].value)
                    if idInt in classes:
                        lektieIDs.append(idInt)
                except:
                    pass

        # Sanitize predays
        try:
            predays = int(arguments['predays'].value)
        except:
            predays = 1

        # Sanitize days
        try:
            days = int(arguments['days'].value)
        except:
            days = 30

        data = getLektier(dbc, lektieIDs, predays, days)

        # Print lektier
        print '    <h1>Lektier for', ', '.join([classes[i] for i in lektieIDs]), '</h1>'
        for d in data:
            if d['hit']:
                dayHeader = d['day'].strftime('%A d. %-d.%-m.').capitalize()
                # day class dependonds on before today, today or in the future
                if d['delta'] < -1: # Old day
                    dayClass = 'oldday'
                elif d['delta'] == -1: # Today
                    dayClass = 'today'
                elif d['delta'] == 0: # Tomorrow
                    dayClass = 'nextday'
                elif datetime.date.today().weekday() >= 4 and d['delta'] < 7 - datetime.date.today().weekday(): # Weekend, extend to monday
                    dayClass = 'nextday'
                else: # A day in the future
                    dayClass = 'day'

                print '    <p><span class="' + dayClass + '">' + dayHeader + '</span>'
                print '      <ul>'
                for id in lektieIDs:
                    if d['lektie'][id]:
                        print '        <li><span class="kl">' + classes[id] + '</span>'
                        print '          <ul>'
                        for l in d['lektie'][id]:
                            lektieNoLink = '-'
                            if l[1]:
                                lektieNoLink = re.sub('://', 'CORRUPURL://', l[1])
                                lektieNoLink = re.sub('src="httpCORRUPURL://www.[a-z]+.[a-z]+/ckeditor444/plugins/smiley/images/[a-z_\-0-9]+.gif"', 'src="/fskintra/pict/face.png"', lektieNoLink)
                                lektieNoLink = re.sub('\n', '</br>\n', lektieNoLink)
                            upd_info = ''
                            if l[3]:
                                upd_info = ', opdateret: '+l[3]
                            if l[0] != '-': # Fag != '-'
                                print '            <li><span class="fag">{}</span>: <span class="do">{}</span> <span class="seen">(Set {}{})</span></li>'.format(l[0], lektieNoLink, l[2], upd_info)
                            else:
                                print '            <li><span class="do">{}</span> <span class="seen">(Set {}{})</span></li>'.format(lektieNoLink, l[2], upd_info)

                        print '          </ul>'
                        print '        </li>'
                print '      </ul>'
                print '    </p>'
        print '  </body>'
        print '</html>'

if __name__ == '__main__':
    import os, inspect

    # Insert .. into path
    cmd_folder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0], "..")))
    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    import skoleintra.config
    main(skoleintra.config.LEKTIEDB)
