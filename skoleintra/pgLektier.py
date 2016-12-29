#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
import surllib
import semail
import urllib
import re
import datetime
import os
if len(config.LEKTIEIDS) > 0:
    import pgLektieDB

URL_PREFIX = 'http://%s/Infoweb/Fi/' % config.HOSTNAME
#For debug, long time back:
#URL_MAIN = URL_PREFIX + 'Dagbog/VisDagbog.asp?Periode=skoleaar&'
URL_MAIN = URL_PREFIX + 'Dagbog/VisDagbog.asp?Periode=naestemaaned&'

def wpParseLektier(bs, id):
    '''Get lektier'''

    # Class name is in a h2 somewhere on the page, else giving up finding class name
    try:
        kl = bs.find('h2').string.encode('utf8')
        kl = re.sub(r'^Lektiebog\ ', '', kl)  # Remove initial 'Lektiebog '
        kl = re.sub(r'\ ?kl(\.|asse)?', '', kl)  # Remove kl/kl./klasse at the end
    except:
        config.log('Warning: Failed to get title for kl for id %d, this indicated getting Lektiebog failed.' % id, 0)
        kl = None

    # Data for each day are located in a <html><body> as <p>'s after each other, Store the <p>'s in daysData
    # A <p> for a day contains 2 tables:
    # - First table contains a h4 somewhere in the sub-tree with date info
    # - Second table contains the data
    # Skip parsing if found text saying there are no homework
    if re.findall('Der\ er\ ingen\ dagbogsblade\ for\ den\ valgte\ periode.', '%s' % bs.html.body, re.MULTILINE):
        return kl, []
    daysData = bs.html.body.findAll('p', recursive=False)
    res = []
    for dayData in daysData:
        tables = dayData.findAll('table', recursive=False)
        tags = tables[1].findAll(recursive=False)

        match_date = ''
        if tables[0].find('h4'):
            match_date = re.search(
                '.*?(?P<weekday>[MTOTFLS][a-z]+dag) den (?P<day>[0-9]{2})-(?P<month>[0-9]{2})-(?P<year>[0-9]{4}):',
                tables[0].find('h4').string)
        # DataTable - Lektier for one day, fag: Lektier in sub<table>, attachments in <menu>:, tables[1]
        fag = {}
        notes = []
        # Find the divs - used for notes in tables[1].tr[1].td[1]
        divNotes = tables[1].findAll('tr', recursive=False)[1].findAll('td', recursive=False)[1].findAll('div', recursive=False)
        for n in divNotes:
            ns = '%s' % n
            if ns:
                ns = re.sub('^<div>', '', ns) # Remove initial <div>
                ns = re.sub('</div>$', '', ns) # Remove trailing </div>
                ns = re.sub('^(&nbsp;| | )*', '', ns) # Minimize empty/invisible content in start
                ns = re.sub('(&nbsp;| | )*$', '', ns) # Minimize empty/invisible content in end

            if ns:
                add_note = True
                for general_note in config.LEKTIE_GENERAL_NOTES:
                    if re.search(general_note, ns, re.IGNORECASE):
                        add_note = False
                if add_note:
                    notes.append(ns)
        attachmentsRaw = tables[1].find('menu')
        attachments = []
        if attachmentsRaw:
            # Access attachment: a['href'], a.string
            atturls = [a['href'] for a in attachmentsRaw.findAll('a')]
            for url in atturls:
                if (
                        config.LEKTIEDB_ATTACHMENT_ROOT # storing attachments saved (LEKTIEDB_ATTACHMENT_ROOT defined)
                        and
                        (url.startswith('/') or config.HOSTNAME in url) # Onsite
                        and
                        config.LEKTIEDB_ATTACHMENT_EXT # Name match defined
                        and
                        re.match('.*[a-zA-Z0-9]\.(' + config.LEKTIEDB_ATTACHMENT_EXT + ')$', url) # url extension matches LEKTIEDB_ATTACHMENT_EXT
                ):
                    # Where should the attachment be saved for LektieWeb
                    fileRelPath = '' # '/' is appended below (part of url)
                    if url.startswith('/'):
                        fileRelPath += url
                    elif url.startswith(config.HOSTNAME):
                        fileRelPath += re.sub(r'^.*' + config.HOSTNAME, '', url) # Skip initial httpX://HOSTNAME
                    else:
                        config.log(u'Lektier:ID=%d: Kan ikke fjerne url til efter hostname for flg. URL: %s' %
                                   (id,
                                    url))
                    fileRelPath = fileRelPath.encode("UTF-8")
                    fileAbsPath = config.LEKTIEDB_ATTACHMENT_ROOT + fileRelPath
                    fileAbsDir = os.path.dirname(fileAbsPath)
                    urlRelLink = '<a href="attachments'+ fileRelPath +'">' + os.path.basename(url) + '</a>'

                    if os.path.exists(fileAbsPath):
                        # The attachment have been downloaded, just mention it so we know it still is attached
                        attachments.append(urlRelLink)
                    else:
                        # If the attachment does not exist, try to download it
                        data = None
                        try:
                            data = surllib.skoleGetURL(url, False)
                        except:
                            # unable to fetch URL
                            config.log(u'Lektier:ID=%d: Kan ikke hente flg. URL: %s' %
                                       (id,
                                        url))
                        if data:
                            try:
                                if not os.path.exists(fileAbsDir):
                                    os.makedirs(fileAbsDir)
                                f = open(fileAbsPath,'w')
                                f.write(data)
                                f.close()
                                attachments.append(urlRelLink)
                            except:
                                config.log(u'Lektier:ID=%d: Kan ikke gemme attachment: %s' %
                                           (id,
                                            fileRelPath))
                                attachments.append(url)
                        else:
                            attachments.append(url)
                else: # Off-site attachment
                    attachments.append(url)
        try:
            for j in xrange(1, len(tables[1].find('table').tbody.findAll('tr'))):
                entr = tables[1].find('table').tbody.findAll('tr')[j].findAll('td')
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
            entr = tables[1]
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
            'notes'   : notes,
            'attachments' : attachments,
        })

    return kl, res

def beautifyFagName(fag):
    fag = fag.title()
    if re.search('Dan', fag, re.IGNORECASE):
        return 'Dan'
    elif re.search('Mat', fag, re.IGNORECASE):
        return 'Mat'
    elif re.search('Eng', fag, re.IGNORECASE):
        return 'Eng'
    elif re.search('Hist', fag, re.IGNORECASE):
        return 'Hist'
    elif re.search('Geo', fag, re.IGNORECASE):
        return 'Geo'
    elif re.search('Bio', fag, re.IGNORECASE):
        return 'Bio'
    elif re.search('Bil', fag, re.IGNORECASE):
        return 'Bil'
    elif re.search('Nat', fag, re.IGNORECASE):
        return 'Nat'
    elif re.search('Samf', fag, re.IGNORECASE):
        return 'Samf'
    elif re.search('Tysk', fag, re.IGNORECASE):
        return 'Tysk'
    elif re.search('Fysik/Kemi', fag, re.IGNORECASE):
        return 'Fysik/Kemi'
    elif re.search('Nat.*Tek', fag, re.IGNORECASE):
        return 'Nat/Tek'
    else:
        return fag

def shortWeekdayString(date):
    weekday = date.isoweekday()
    if weekday == 1:
        return 'M'
    if weekday == 2:
        return 'Ti'
    if weekday == 3:
        return 'O'
    if weekday == 4:
        return 'To'
    if weekday == 5:
        return 'F'
    if weekday == 6:
        return 'L'
    if weekday == 7:
        return 'S'
    else:
        return '?'

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
        # Notes
        if lektier[i]['notes']:
            res += '**** Noter:\n'
            for data in lektier[i]['notes']:
                res += '- %s\n' % data
        # Attachments
        if lektier[i]['attachments']:
            res += '**** Bilag:\n'
            res += 'Se på forældreintra eller elevintra, filerne er:' + "\n"
            for data in lektier[i]['attachments']:
                udata = data + "\n" if isinstance(data, unicode) else data.string.encode('utf8') + "\n"
                # Skip <a href.. >, only leave text (filename)
                udata = re.sub(r'^<a href="attachments[^>]*>','', re.sub(r'</a>$','', udata))
                res += '- ' + udata
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
            # Format content for a day (part after <Day:>), store it in dayContent
            dayContent = ''
            for fag, lektie in lektier[i]['lektier'].items():
                if lektie:
                    fagStr = fag + ': '
                    lektieStr = re.sub("<.*?>", "", lektie)
                    lektieStr = lektieStr.replace("\n", "\n" + ''.ljust(len(fagStr)))
                    dayContent += fagStr + lektieStr + "\n"

            if dayContent: # Content for that day
                # Lektier for that day
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
                res += dayContent
    res = res.rstrip() # Remove trailing \n
    return res

def getLektieLister(ids = config.LEKTIEIDS):
    global bs

    if len(config.LEKTIEIDS) == 0:
        config.log('Info: For at hente lektier: Adder linie i config filen: "lektieids=[1, 2, 3]"')
        config.log('Info- hvor tallene er ID=<num> for din(e) barn/børn i url\'en for Lektier')

    klAll = {}
    lektierAll = {}
    for id in ids:
        # surllib.skoleLogin()
        config.log('Kigger efter opdaterede lektier for id %d, og gemmer i lektiedatabasen' % id)

        # read the initial page
        url = URL_MAIN + "ID=%d" % id
        bs = surllib.skoleGetURL(url, True, True)
        #f = open('/tmp/a.html', 'r')
        #bs = surllib.beautify(f.read())

        if False:
            fh = open('/tmp/a.html', 'w')
            fh.write(str(bs))
            fh.close()
        try:
            kl, lektier = wpParseLektier(bs, id)
        except:
            kl = None
            config.log('''Error parsing lektier for kl. at url: '%s'.''' % (url), 0)
        if not kl:
            config.log('''Error: Class name couldn\'t be read from title at url: '%s'.''' % (url))
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
    getLektieLister([25])
    pass
