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
    sql = 'create table if not exists lektier     (id integer, day date, fag text, lektie text, created datetime, updated datetime)'
    c.execute(sql)
    sql = 'create table if not exists notes       (id integer, day date, i integer, data text,  created datetime, updated datetime)'
    c.execute(sql)
    sql = 'create table if not exists attachments (id integer, day date, i integer, data text,  created datetime, updated datetime)'
    c.execute(sql)

    return conn, c

def updateLektieDb(id, kl, lektier):
    '''Update lektie DB with new? content'''
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
        # Fag:Lektier
        for fag, lektie in lektier[i]['lektier'].items():
            insert_or_update_db(conn, c, 'lektier', id, day, 'fag', 'lektie', fag, lektie)
        # i:Notes & i:Attachments
        for table in ['notes', 'attachments']:
            for j in xrange(len(lektier[i][table])):
                insert_or_update_db(conn, c, table, id, day, 'i', 'data', j, lektier[i][table][j])

def insert_or_update_db(conn, c, dbtable, id, day, key_name, value_name, key, value):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # There is a problem if a note is removed (last note will remain unchanged, and others will be overwritten) or inserted (only seen/updated timestamps are wrong)
    # E.g.:
    # Old:
    # i=0 val=A
    # i=1 val=B
    # New: Line with A is removed
    # i=0 val=B (updated)
    # i=1 val=B (untouched)
    # New: Line with A0 insterted after A
    # i=0 val=A (untouched)
    # i=1 val=A1 (updated)
    # i=2 val=B (new)
    d = (id, day, key, )
    c.execute('SELECT * FROM %s WHERE id=? and day=? and %s=?' % (dbtable, key_name), d)
    r = c.fetchone()
    if not r:
        if value:
            # Not existing, add it
            d = (id, day, key, value, now, )
            c.execute('INSERT INTO %s VALUES (?,?,?,?,?, Null)' % (dbtable), d)
            conn.commit()
    elif r[3] != value:
        # Update value for given id, day, key
        d = (value, now, id, day, key, )
        c.execute('UPDATE %s set %s=?, updated=? where id=? and day=? and %s=?' % (dbtable, value_name, key_name), d)
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

    for delta_days in xrange(-100, 100):
        # Day
        day = datetime.date.today() + datetime.timedelta(days=delta_days)
        # Select lektier for day
        entries_found_for_day = False # Any lektier for day?
        lektie = {}
        notes = {}
        attachments = {}
        for id in config.LEKTIEIDS:
            d = (id, day,)
            # Fetch lektier
            c.execute('SELECT fag, lektie, created, updated FROM lektier where id=? and day=?', d)
            lektie[id] = c.fetchall()
            if lektie[id]:
                entries_found_for_day = True
            # Fetch notes
            c.execute('SELECT i, data, created, updated FROM notes where id=? and day=?', d)
            notes[id] = c.fetchall()
            if notes[id]:
                entries_found_for_day = True
            # Fetch attachments (urls)
            c.execute('SELECT i, data, created, updated FROM attachments where id=? and day=?', d)
            attachments[id] = c.fetchall()
            if attachments[id]:
                entries_found_for_day = True
        # Print
        if entries_found_for_day:
            dayHeader = day.strftime('%A d. %-d.%-m.').capitalize()
            print '** '+dayHeader
            for id in config.LEKTIEIDS:
                if lektie[id] or notes[id] or attachments[id]:
                    print '*** '+classes[id]
                    if lektie[id]:
                        print '**** Lektier'
                    for l in lektie[id]:
                        upd_info = ''
                        if l[3]:
                            upd_info = 'opdateret: '+l[3]
                        print '- {}: {}\n(Set {})'.format(l[0], l[1], l[2], upd_info)
                    if notes[id]:
                        print '**** Noter'
                    for l in notes[id]:
                        upd_info = ''
                        if l[3]:
                            upd_info = 'opdateret: '+l[3]
                        print '- {}: {}\n(Set {})'.format(l[0], l[1], l[2], upd_info)
                    if attachments[id]:
                        print '**** Attachments'
                    for l in attachments[id]:
                        upd_info = ''
                        if l[3]:
                            upd_info = 'opdateret: '+l[3]
                        print '- {}: {}\n(Set {})'.format(l[0], l[1], l[2], upd_info)

    # Integrate reading attachments
    #c.execute('SELECT * FROM attachments')
    #print c.fetchall()
