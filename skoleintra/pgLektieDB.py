#
# -*- encoding: utf-8 -*-
#

import re
import datetime
import sqlite3
import sys
import pgLektier
import config

def connectDb():
    try:
        conn = sqlite3.connect(config.LEKTIEDB)
        c = conn.cursor()
    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)

    # Create tables if missing
    sql = 'create table if not exists classes (id integer, class text)'
    c.execute(sql)
    sql = 'create table if not exists lektier (id integer, day date, fag text, lektie text, created datetime, updated datetime)'
    c.execute(sql)
    #sql = 'create table if not exists attachments (id integer, day date, attachment text, created datetime, updated datetime)'
    #c.execute(sql)

    return conn, c

def updateLektieDb(id, kl, lektier):
    '''Update lektie DB with new? content'''
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn, c = connectDb()

    # kl: Set/Update/leave if unchanged
    d = (id,)
    c.execute('SELECT * FROM classes WHERE id=?', d)
    r = c.fetchone()
    if not r:
        # Not existing, add it
        d = (id,kl)
        c.execute('INSERT INTO classes VALUES (?,?)', d)
        conn.commit()
    elif r[1] != kl:
        # Update kl
        d = (kl, id)
        c.execute('UPDATE classes set class = ? where id = ?', d)
        conn.commit()

    # lektier: Set/Update/leave if unchanged
    for i in xrange(len(lektier) -1, -1, -1): # Rev-range since newest is the first on forældreintra
        day = lektier[i]['day'].strftime("%Y-%m-%d")
        for fag, lektie in lektier[i]['lektier'].items():
            d = (id, day, fag, )
            c.execute('SELECT * FROM lektier WHERE id=? and day=? and fag=?', d)
            r = c.fetchone()

            if not r:
                if lektie:
                    # Not existing, add it
                    d = (id, day, fag, lektie, now, )
                    c.execute('INSERT INTO lektier VALUES (?,?,?,?,?, Null)', d)
                    conn.commit()
            elif r[3] != lektie:
                # Update lektie for given id, day, fag
                d = (lektie, now, id, day, fag, )
                c.execute('UPDATE lektier set lektie=?, updated=? where id=? and day=? and fag=?', d)
                conn.commit()

if __name__ == '__main__':
    # test reading from DB
    pass

    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    conn, c = connectDb()

    c.execute('SELECT * FROM classes')
    classes = {}
    for id, kl in c.fetchall():
        classes[id] = kl
    pp.pprint(classes)

    import locale

    # Let's set danish locale
    locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')

    for delta_days in xrange(30):
        # Day
        day = datetime.date.today() + datetime.timedelta(days=delta_days)
        # Select lektier for day
        entries_found_for_day = False # Any lektier for day?
        lektie = {}
        for id in config.LEKTIEIDS:
            d = (id, day,)
            c.execute('SELECT fag, lektie, created, updated FROM lektier where id=? and day=?', d)
            lektie[id] = c.fetchall()
            if lektie[id]:
                entries_found_for_day = True

        # Print
        if entries_found_for_day:
            dayHeader = day.strftime('%A d. %-d.%-m.').capitalize()
            print '** '+dayHeader
            for id in config.LEKTIEIDS:
                if lektie[id]:
                    print '*** '+classes[id]
                    for l in lektie[id]:
                        upd_info = ''
                        if l[3]:
                            upd_info = 'opdateret: '+l[3]
                        print '- {}: {}\n(Set {})'.format(l[0], l[1], l[2], upd_info)

    # Integrate reading attachments
    #c.execute('SELECT * FROM attachments')
    #print c.fetchall()
