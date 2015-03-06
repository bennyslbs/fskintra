#
# -*- encoding: utf-8 -*-
#

import config
import surllib
import semail
import urllib
import re
import datetime

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
                    entr[k] = entr[k].decode("UTF-8").strip()
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

def shortWeekdayString(date):
    weekday = date.isoweekday()
    if weekday == 1:
        return u'M'
    if weekday == 2:
        return u'Ti'
    if weekday == 3:
        return u'O'
    if weekday == 4:
        return u'To'
    if weekday == 5:
        return u'Fr'
    if weekday == 6:
        return u'L'
    if weekday == 7:
        return u'S'
    else:
        return u'?'

def wpOrgPrintLektier(title, lektier):
    res = '**' + title + "\n"
    for i in xrange(len(lektier) -1, 0, -1): # Rev-range since newest is the first on forældreintra
        res += "*** %s d. %4d.%02d.%02d\n" % (lektier[i]['weekday'], lektier[i]['year'], lektier[i]['month'], lektier[i]['day'])
        for fag, lektie in lektier[i]['lektier'].items():
            res += '- ' + beautifyFagName(fag) + ': ' + lektie + "\n"
    return res

def wpFormatSMSLektier(title, lektier, days):
    res = ''
    weekday = datetime.date.today().isoweekday()
    if weekday == 5 and days < 7: # It's friday, add 2 days to days if <7
        days += 2
    today = datetime.date.today()
    otherDate = datetime.date(2015, 12, 31)
    # Tomorrow
    for i in xrange(len(lektier) -1, 0, -1): # Rev-range since newest is the first on forældreintra
        lektieDay = datetime.date(lektier[i]['year'], lektier[i]['month'], lektier[i]['day'])
        delta = (lektieDay - today).days
        if (delta >= 1 and delta <= days):
            # Print date info, differs depending how many days from now
            if delta == 1:
                # Tomorrow - no date info
                pass
            elif delta < 7:
                # Within next week: Just a short for the week day
                res += shortWeekdayString(lektieDay) + ":\n"
            else:
                # Afer next week: A short for the week day + How many weeks, e.g. To1
                res += shortWeekdayString(lektieDay) + str(int(delta/7)) + ":\n"

            # Print lektie
            for fag, lektie in lektier[i]['lektier'].items():
                res += '' + beautifyFagName(fag) + ': ' + lektie + "\n"
    res = res.rstrip() # Remove trailing \n
    return res

def skoleLektier(id):
    global bs

    # surllib.skoleLogin()
    config.log(u'Kigger efter nye lektier for id %d' % id)

    # read the initial page
    bs = surllib.skoleGetURL(URL_MAIN + "ID=%d" % id, True, True)

    if True:
        fh = open('/tmp/a.html', 'w')
        fh.write(str(bs))
        fh.close()
    title, lektier = wpParseLektier(bs)
    print wpOrgPrintLektier(title, lektier)
    print wpFormatSMSLektier(title, lektier, 1)

def getLektieLister(lektieIds):
    if len(lektieIds) == 0:
        config.log(u'Info: For at hente lektier: Adder linie i config filen: "lektieids=[1, 2, 3]"')
        config.log(u'Info- hvor tallene er ID=<num> for din(e) barn/børn i url\'en for Lektier')
    for id in lektieIds:
        skoleLektier(id)

if __name__ == '__main__':
    # test
    #skoleLektier(22)

    f = open('/tmp/a.html', 'r')
    title, lektier = wpParseLektier(surllib.beautify(f.read()))
    print "# Org-mode formatted content ###########################################"
    print wpOrgPrintLektier(title, lektier)
    print "# SMS content ##########################################################"
    print wpFormatSMSLektier(title, lektier, 7)
