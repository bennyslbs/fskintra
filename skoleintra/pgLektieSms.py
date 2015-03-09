#
# -*- encoding: utf-8 -*-
#

import config
import pgLektier
import urllib

# Send a SMS with llektier
def sendSms():
    txt = pgLektier.skoleLektierSmsTxt(config.SMS_ID, config.SMS_DAYS, config.SMS_MIN_MSGS_DAYS)

    # if-elif with all supported SMS gateways
    if config.SMS_GW == 'smsit.dk':
        url = 'http://www.smsit.dk/api/sendSms.php'
        params = urllib.urlencode({
            'apiKey': config.SMS_KEY,
            'senderId': config.SMS_FROM,
            'mobile': '45' + config.SMS_TO,
            'message': txt.encode('utf-8'),
        })
    else:
        config.log(u'Error: Ukendt/ej implementeret SMS_GW: "'+ config.SMS_GW + '". Implementer det i pgLektieSMS.py')
        return -1

    # Send SMS if non-empty
    if txt!= '':
        # Debug
        print "Dbg: url:", url
        print "Dbg: params:", params
        f = urllib.urlopen(url, params)
        status = int(f.read())
        config.log(
            u'Info: SMS sendt til [%s] med status %d.' % ('sms-'+config.SMS, status))
        return status
    else:
        config.log(
            u'Info: Ingen SMS sendt pga. listen af \'relevante\' lektier er tom for [%s]' % ('sms-'+config.SMS))
        return 0
