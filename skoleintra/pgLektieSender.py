#
# -*- encoding: utf-8 -*-
#

import config
import pgLektier
import urllib
import re
import smtplib
import sys
import os

# Only required if sending SMS via gw=smsgw
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../3rdparty/smsgw')
import smsgw

def sendEmailMsg(subj, recip, msg):
    '''Copy + slighlty modified from semail send()'''
    config.log(u'Sender email for %s to %s' %
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

def sendSmsMsg(sms_grp, sms_cfg, to, msg):
    status = -1
    statusStr = ''

    # if-elif with NoSMSGW and all supported SMS gateways
    if sms_cfg['smsgw']['gw'] == 'smsgw':
        gw = smsgw.smsgw(sms_cfg['smsgw']['host'], int(sms_cfg['smsgw']['port']))

        params = {}
        params['priority'] = sms_cfg['smsgw']['priority']
        params['gw']       = sms_cfg['smsgw']['smsgwgw']
        params['from']     = sms_cfg['from']
        params['to']       = to
        params['msg']      = msg.encode('utf-8')
        params['GetDeliveryReport'] = sms_cfg['smsgw']['GetDeliveryReport']
        params['verbose'] = False

        resp = gw.send_sms(params)
        code = resp.pop('code')
        keys = resp.keys()
        if len(keys) == 1 and 'msg' in keys: # Exact one key, the msg key
            msg = resp['msg']
        else:
            msg = json.dumps(resp)
        return code, msg
    elif sms_cfg['smsgw']['gw'] == 'NoSMSGW':
        return 0, u'Info: SMS not sent to %s since NoSMSGW is used for \'%s\'' % (to, 'sms-'+sms_grp)
    elif sms_cfg['smsgw']['gw'] == 'smsit.dk':
        url = 'http://www.smsit.dk/api/sendSms.php'
        params = urllib.urlencode({
            'apiKey': sms_cfg['smsgw']['key'],
            'senderId': sms_cfg['from'],
            'mobile': '45' + to,
            'message': msg.encode('utf-8'),
        })
        # Send
        try:
            f = urllib.urlopen(url, params)
        except:
            return -1, u'Error: Can\'t connect to SMS Gateway for \'%s\'' % ('sms-'+sms_grp)
        statusStr = f.read()
        status = int(statusStr)
    elif sms_cfg['smsgw']['gw'] == 'eu.apksoft.android.smsgateway':
        url = sms_cfg['smsgw']['url']
        params = urllib.urlencode({
            'password': sms_cfg['smsgw']['key'],
            'phone': to,
            'text': msg.encode('utf-8'),
        })
        # Send
        try:
            f = urllib.urlopen(url + '?' + params)
        except:
            return -1, u'Error: Can\'t connect to SMS Gateway for \'%s\'' % ('sms-'+sms_grp)
        statusStr = f.read()

        statusStr = statusStr.replace('\n', '')

        match = re.search(
            '.*?<body>(?P<body>.*)</body>.*',
            statusStr)
        statusStr = match.group('body')
        statusStr = statusStr.replace('<br/>', '\n').rstrip()

        if statusStr == 'Mesage SENT!': # Status from GW is misspelled.
            status = 0
        elif statusStr == 'Invalid parameters':
            status = 1
        else:
            status = 28
    else:
        retrun -1, u'Error: Ukendt/ej implementeret SMS_GW: "'+ sms_cfg['smsgw]']['gw'] + '". Implementer det i sendSmsMsg i pgLektieSender.py'

    # Return SMS status, 0 ok, !=0 maybe error, something went wrong
    tried_to_send_str = ''
    if status != 0:
        tried_to_send_str = 'forsøgt '
    return status, u'SMS ' + tried_to_send_str + 'sendt til [%s]: %s med status %d (%s).' % ('sms-'+sms_grp, to, status, statusStr)

# Send Emails and SMS's with lektier
def sendEmailSms(klAll, lektierAll):
    for sms_grp, sms_cfg in config.SMS.iteritems():
        # Find which to email and SMS to (split to -> email_to + sms_to)
        email_to = []
        sms_to = []
        for recip in sms_cfg['to'].split('\n'):
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

        # Find lektier for the group
        if sms_cfg['id'] in klAll and sms_cfg['id'] in lektierAll:
            config.log(u'Sender til lektie gruppe ['+sms_grp+']')
            kl, emailtxt, smstxt = pgLektier.formatLektier(klAll[sms_cfg['id']], lektierAll[sms_cfg['id']], sms_cfg['days'], sms_cfg['min_msgs_days'])
        elif (len(email_to) + len(sms_to)) > 0:
            config.log(u'Warning: Can\'t send to lektie group [%s], since lektier for ID %d havn\'t been fetched' % (sms_grp, sms_cfg['id']), 0)
            return
        else:
            config.log(u'Warning: Can\'t send to empty lektie group [%s], since lektier for ID %d havn\'t been fetched' % (sms_grp, sms_cfg['id']), 1)
            return

        # Seems ok, (klAll, lektierAll contains ID), send Email+SMS
        # Send emails
        if len(email_to) != 0:
            if emailtxt != '':
                sendEmailMsg('Lektier: %s' % (kl), email_to, emailtxt)
            else:
                config.log(
                    u'Info: Ingen Email sendt pga. listen af \'relevante\' lektier er tom for lektie gruppe ['+sms_grp+']')

        # Send SMSes
        if len(sms_to) != 0: # Any receivers and a
            if smstxt != '': # Any message to send
                for recip in sms_to:
                    try:
                        config.log(u'SMS to %s: Length: %d(%f): "%s"' % (recip, len(smstxt), len(smstxt)/160.0, smstxt), 2)
                        status, msg = sendSmsMsg(sms_grp, sms_cfg, recip, smstxt)
                        if status != 0:
                            config.log(msg, 0)
                        else:
                            config.log(msg)
                    except:
                        config.log('Failed to send sms to [%s]: %s' % (sms_grp, recip))
            else:
                config.log(
                    u'Info: Ingen SMS sendt pga. listen af \'relevante\' lektier er tom for lektie gruppe ['+sms_grp+']')
