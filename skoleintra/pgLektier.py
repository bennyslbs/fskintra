#
# -*- encoding: utf-8 -*-
#

import config
import surllib
import semail
import urllib
import re
import datetime
if len(config.LEKTIEIDS) > 0:
    import pgLektieDB

URL_PREFIX = 'http://%s/Infoweb/Fi/' % config.HOSTNAME
URL_MAIN = URL_PREFIX + 'Dagbog/VisDagbog.asp?Periode=naestemaaned&'

def wpParseLektier(bs, id):
    '''Get lektier'''
    try:
        kl = bs.find('h2').string.encode('utf8')
        kl = re.sub(r'^Lektiebog\ ', '', kl)  # Remove initial 'Lektiebog '
        kl = re.sub(r'\ ?kl(\.|asse)?', '', kl)  # Remove kl/kl./klasse at the end
    except:
        config.log(u'Warning: Failed to get title for kl for id %d, this indicated getting Lektiebog failed.' % id, 0)
        kl = None

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
            try:
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
                    if len(entr) == 2: # Sometimes entr[1] is mission - seen if table boundraries are missing and no homework for fag.
                        if entr[0] != None:
                            fag[beautifyFagName(entr[0])] = entr[1]
            except:
                # Just one entry ... or don't try to split it
                entr = maint[i +1]
                # Get content
                entr = entr.renderContents().strip()
                #entr = entr.replace(' ', '') # Invisible/&nbsp like char
                entr = re.sub(r'<td.*?>(&nbsp;| | )*</td>', '<td></td>', entr) # Minimize empty/invisible content td's
                entr = re.sub(r'<tr.*?>(<td.*?>(&nbsp;| )*</td>)*</tr>', '', entr) # Remove empty table rows
                entr = entr.replace("<div>", "").replace("</div>", "") # Remove <div>
                entr = entr.replace("&amp;", "&") # Replace some html escaping
                entr = entr.decode("UTF-8").strip()
                if entr == '':
                    entr = None
                if entr != None:
                    fag['-'] = entr
            res.append({
                'day' : datetime.date(int(match_date.group('year')), int(match_date.group('month')), int(match_date.group('day'))),
                'weekday' : match_date.group('weekday'),
                'lektier' : fag,
                'attachments' : attachments,
            })

            # # To access the attachments:
            # if attachments:
            #     for a in attachments:
            #         print "Dbg:", a['href'], a.string

    return kl, res

def beautifyFagName(fag):
    fag = fag.title()
    if fag == 'Dansk':
        return 'Dan'
    elif fag == 'Matematik':
        return 'Mat'
    elif fag == 'Engelsk':
        return 'Eng'
    elif fag == 'Historie':
        return 'Hist'
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
        return u'F'
    if weekday == 6:
        return u'L'
    if weekday == 7:
        return u'S'
    else:
        return u'?'

def wpOrgPrintLektier(kl, lektier):
    res = ''
    if len(lektier) > 0:
        res += '** ' + kl + "\n"
    for i in xrange(len(lektier) -1, -1, -1): # Rev-range since newest is the first on forældreintra
        res += "*** %s d. %s\n" % (lektier[i]['weekday'], lektier[i]['day'].strftime("%d.%m.%Y"))
        for fag, lektie in lektier[i]['lektier'].items():
            if lektie:
                if fag != '-':
                    fagStr = '- ' + fag + ': '
                    lektieStr = lektie
                else:
                    # Special case: No fag name, also remove tr and td's (both start+end)
                    fagStr = '- '
                    lektieStr = re.sub("<\/?(tr|td).*?>", "", lektie)
                lektieStr = lektieStr.replace("\n", "\n" + ''.ljust(len(fagStr)))
                res += fagStr + lektieStr + "\n"

    return res.encode('utf8')

def wpFormatSMSLektier(kl, lektier, days, minMsgDays = 0):
    '''Format compact string intended for SMS with lektier for days,
    extend so that lektier for minMsgDays is returned'''
    res = ''
    weekday = datetime.date.today().isoweekday()
    # If first weekend is included in days - add 2 days
    if ((weekday == 5)
        and (weekday == 4 and days > 1)
        and (weekday == 3 and days > 2)
        and (weekday == 2 and days > 3)
        and (weekday == 1 and days > 4)
    ):
        days += 2
    # For each following weekend, add 2 days
    if days > 7:
        days += 2 * int((days -7)/5) # -7 since first week is handled special above
    today = datetime.date.today()
    msgDays = 0;
    for i in xrange(len(lektier) -1, -1, -1): # Rev-range since newest is the first on forældreintra
        lektieDay = lektier[i]['day']
        delta = (lektieDay - today).days
        if delta >= 1 and (delta <= days or msgDays < minMsgDays):
            msgDays += 1
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
                if lektie:
                    fagStr = fag + ': '
                    lektieStr = re.sub("<.*?>", "", lektie)
                    lektieStr = lektieStr.replace("\n", "\n" + ''.ljust(len(fagStr)))
                    res += fagStr + lektieStr + "\n"
    res = res.rstrip() # Remove trailing \n
    return res

def getLektieLister():
    global bs

    if len(config.LEKTIEIDS) == 0:
        config.log(u'Info: For at hente lektier: Adder linie i config filen: "lektieids=[1, 2, 3]"')
        config.log(u'Info- hvor tallene er ID=<num> for din(e) barn/børn i url\'en for Lektier')

    klAll = {}
    lektierAll = {}
    for id in config.LEKTIEIDS:
        # surllib.skoleLogin()
        config.log(u'Kigger efter opdaterede lektier for id %d, og gemmer i lektiedatabasen' % id)

        # read the initial page
        url = URL_MAIN + "ID=%d" % id
        bs = surllib.skoleGetURL(url, True, True)
        #f = open('/tmp/a.html', 'r')
        #bs = surllib.beautify(f.read())

        if True:
            fh = open('/tmp/a.html', 'w')
            fh.write(str(bs))
            fh.close()
        try:
            kl, lektier = wpParseLektier(bs, id)
        except:
            kl = None
            config.log(u'Error parsing lektier for kl.', 0)
        if not kl:
            config.log(u'''Error: Class name couldn\'t be read from title at url: '%s'.''' % (url))
        # Fill content into DB
        if kl: # If kl = None it is an illegal ID (no header, so propably illegal ID)
            pgLektieDB.updateLektieDb(id, kl, lektier)
            klAll[id] = kl
            lektierAll[id] = lektier
    return klAll, lektierAll

def formatLektier(kl, lektier, sms_days=1, sms_min_msgs_days=0):
    return \
        kl, \
        wpOrgPrintLektier(kl, lektier), \
        wpFormatSMSLektier(kl, lektier, sms_days, sms_min_msgs_days)

if __name__ == '__main__':
    pass
