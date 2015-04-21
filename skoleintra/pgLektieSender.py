#
# -*- encoding: utf-8 -*-
#

import config
import pgLektier
import urllib
import re
import smtplib

def sendEmailMsg(subj, recip, msg):
    '''Copy + slighlty modified from semail send()'''
    config.log(u'Sender email %s to %s' %
               (subj, recip))

    # open smtp connection
    if config.SMTPHOST:
        server = smtplib.SMTP(config.SMTPHOST, config.SMTPPORT)
    else:
        server = smtplib.SMTP('localhost')
    # server.set_debuglevel(1)
    if config.SMTPLOGIN:
        try:
            server.starttls()
        except SMTPException:
            pass  # ok, but we tried...
        server.login(config.SMTPLOGIN, config.SMTPPASS)
    server.sendmail(config.SENDER, recip, 'Subject: '+subj+'\nReply-To: Benny Simonsen <benny@slbs.dk>\nTo: LektieEmail modtagere\n\n'+msg)
    server.quit()

def sendSmsMsg(to, msg):
    status = -1
    statusStr = ''

    # if-elif with all supported SMS gateways
    if config.SMS_GW == 'smsit.dk':
        url = 'http://www.smsit.dk/api/sendSms.php'
        params = urllib.urlencode({
            'apiKey': config.SMS_KEY,
            'senderId': config.SMS_FROM,
            'mobile': '45' + to,
            'message': msg.encode('utf-8'),
        })
        # Debug
        #print "Dbg: url:", url
        #print "Dbg: params:", params
        # Send
        f = urllib.urlopen(url, params)
        statusStr = f.read()
        status = int(statusStr)
    elif config.SMS_GW == 'eu.apksoft.android.smsgateway':
        url = config.SMS_URL + '?password='+config.SMS_KEY + '&phone='+to + '&text='+msg.encode('utf-8')
        # Debug
        #print "Dbg: url:", url
        # Send
        f = urllib.urlopen(url)
        statusStr = f.read()

        statusStr = statusStr.replace('\n', '')

        match = re.search(
            '.*?<body>(?P<body>.*)</body>.*',
            statusStr)
        statusStr = match.group('body')
        statusStr = statusStr.replace('<br/>', '\n').rstrip()

        if statusStr == 'Mesage SENT!':
            status = 0
        elif statusStr == 'Invalid parameters':
            status = 1
        else:
            status = 28
    else:
        retrun -1, u'Error: Ukendt/ej implementeret SMS_GW: "'+ config.SMS_GW + '". Implementer det i sendSmsMsg i pgLektieSender.py'

    # Send SMS if non-empty
    return status, u'Info: SMS sendt til [%s]: %s med status %d (%s).' % ('sms-'+config.SMS, to, status, statusStr)

# Send Emails and SMS's with lektier
def sendEmailSms():
    title, emailtxt, smstxt = pgLektier.skoleLektier(config.SMS_ID, config.SMS_DAYS, config.SMS_MIN_MSGS_DAYS)

    email_to = []
    sms_to = []
    for recip in config.SMS_TO.split('\n'):
        recip = recip.lstrip().rstrip()

        match_comment = re.search('(^$|^#)', recip)
        match_number = re.search('^[0-9]+$', recip)
        match_email = re.search('^.*@.*$', recip)
        if match_comment:
            pass
        elif match_number:
            sms_to.append(recip)
        elif match_email:
            email_to.append(recip)
        else:
            print "Warning: Ignoring invalid line in SMS(SMS or Email) To:", recip

    if len(email_to) != 0:
        if emailtxt != '':
            sendEmailMsg(title, email_to, emailtxt)
        else:
            config.log(
                u'Info: Ingen Email sendt pga. listen af \'relevante\' lektier er tom for [%s]' % ('sms-'+config.SMS))
            return 0
    else:
        return 0

    if smstxt != '':
        for recip in sms_to:
            status, msg = sendSmsMsg(recip, smstxt)
            config.log(msg)
    else:
        config.log(
            u'Info: Ingen SMS sendt pga. listen af \'relevante\' lektier er tom for [%s]' % ('sms-'+config.SMS))
        return 0
