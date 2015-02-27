#
# -*- encoding: utf-8 -*-
#

import config
import surllib
import semail
import urllib
import re

URL_PREFIX = 'http://%s/Infoweb/Fi/' % config.HOSTNAME
URL_MAIN = URL_PREFIX + 'Dagbog/VisDagbog.asp?Periode=naestemaaned&'

def wpParseLektier(bs):
    '''Get lektier'''
    title = bs.find('h2').string

    maint = [t for t in bs.findAll('table')]
    res = []
    for i in xrange(len(maint)):
        if maint[i].find('h4'):
            match_date = re.search(
                '.*?(?P<weekday>[MTOTFLS][a-z]+dag) den (?P<day>[0-9]{2})-(?P<month>[0-9]{2})-(?P<year>[0-9]{4}):',
                maint[i].find('h4').string)
            # Get content in next table
            fag = {}
            attachments = maint[i +1].find('menu')
            if attachments:
                attachments = attachments.findAll('a')
            for j in xrange(1, len(maint[i +1].find('table').tbody.findAll('tr'))):
                entr = maint[i +1].find('table').tbody.findAll('tr')[j].findAll('td')
                # Get content
                for k in xrange(len(entr)):
                    entr[k] = entr[k].renderContents().strip()
                    entr[k] = entr[k].replace("<div>", "").replace("</div>", "") # Remove <div>
                    entr[k] = entr[k].replace("&amp;", "&") # Replace some html escaping
                    entr[k] = entr[k].replace('\xc2\xa0', '') # Special char, looks like blank
                    if entr[k] == '':
                        entr[k] = None
                if entr[0] != None and entr[1] != None:
                    fag[entr[0]] = entr[1]
            res.append({
                'weekday' : match_date.group('weekday'),
                'year' : int(match_date.group('year')),
                'month' : int(match_date.group('month')),
                'day' : int(match_date.group('day')),
                'lektier' : fag,
                'attachments' : attachments,
            })

            # # To access the attachments:
            # if attachments:
            #     for a in attachments:
            #         print "Dbg:", a['href'], a.string

    return title, res

def beautifyFagName(fag):
    fag = fag.title()
    if fag == 'Dansk':
        return 'Dan'
    elif fag == 'Matematik':
        return 'Mat'
    elif fag == 'Engelsk':
        return 'Eng'
    else:
        return fag

def wpFindLektier(bs):
    title, lektier = wpParseLektier(bs)

    print '**', title
    for i in xrange(len(lektier) -1, 0, -1): # Rev-range since newest is the first on forældreintra
        print "*** %s d. %4d.%02d.%02d" % (lektier[i]['weekday'], lektier[i]['year'], lektier[i]['month'], lektier[i]['day'])
        for fag, lektie in lektier[i]['lektier'].items():
            print '- ' + beautifyFagName(fag) + ': ' + lektie

def skoleLektier(id):
    global bs

    # surllib.skoleLogin()
    config.log(u'Kigger efter nye lektier for id %d' % id)

    # read the initial page
    bs = surllib.skoleGetURL(URL_MAIN + "ID=%d" % id, True, True)
    wpFindLektier(bs)

def getLektieLister():
    lektieIds = config.LEKTIEIDS
    if len(lektieIds) == 0:
        config.log(u'Info: For at hente lektier: Adder linie i config filen: "lektieids=[1, 2, 3]"')
        config.log(u'Info- hvor tallene er ID=<num> for din(e) barn/børn i url\'en for Lektier')
    for id in lektieIds:
        skoleLektier(id)

if __name__ == '__main__':
    # test
    #skoleLektier()

    f = open('/tmp/a.html', 'r')
    wpFindLektier(surllib.beautify(f.read()))
