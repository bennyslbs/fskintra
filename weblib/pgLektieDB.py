#
# -*- encoding: utf-8 -*-
#

import re
import datetime
import sqlite3
import sys

def connectDb(db = "/tmp/lektier2.db"):
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)
    return conn, c

def updateLektieDb(id, kl, lektier):
    '''Update lektie DB with new? content'''
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn, c = connectDb()

    # kl: Set/Update/leave if unchanged
    d = (id,)
    c.execute('SELECT * FROM classes WHERE id=?', d)
    r = c.fetchone()
    if kl:
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
