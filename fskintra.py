#! /usr/bin/env python
#
#
#

import skoleintra.config
import skoleintra.pgContactLists
import skoleintra.pgDialogue
import skoleintra.pgDocuments
import skoleintra.pgFrontpage
import skoleintra.pgWeekplans
import skoleintra.pgLektier
import skoleintra.pgLektieSender
import skoleintra.schildren

SKOLEBESTYELSE_NAME = 'Skolebestyrelsen'

cnames = skoleintra.schildren.skoleGetChildren()
if cnames.count(SKOLEBESTYELSE_NAME):
    skoleintra.config.log(u'Ignorerer ['+SKOLEBESTYELSE_NAME+']')
    cnames.remove(SKOLEBESTYELSE_NAME)

for cname in cnames:
    skoleintra.schildren.skoleSelectChild(cname)

    skoleintra.pgContactLists.skoleContactLists()
    skoleintra.pgFrontpage.skoleFrontpage()
    skoleintra.pgDialogue.skoleDialogue()
    skoleintra.pgDocuments.skoleDocuments()
    skoleintra.pgWeekplans.skoleWeekplans()

#skoleintra.pgLektier.getLektieLister(skoleintra.config.LEKTIEIDS)

if skoleintra.config.SMS:
    exit(skoleintra.pgLektieSender.sendEmailSms())
