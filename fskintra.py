#! /usr/bin/env python
#
#
#

import sys
import skoleintra.config
import skoleintra.pgContactLists
import skoleintra.pgDialogue
import skoleintra.pgDocuments
import skoleintra.pgFrontpage
import skoleintra.pgWeekplans
import skoleintra.pgLektier
import skoleintra.pgLektieSender
import skoleintra.schildren

cnames = skoleintra.schildren.skoleGetChildren()
for cname in cnames:
    skoleintra.schildren.skoleSelectChild(cname)

    skoleintra.pgContactLists.skoleContactLists()
    skoleintra.pgFrontpage.skoleFrontpage()
    skoleintra.pgDialogue.skoleDialogue()
    skoleintra.pgDocuments.skoleDocuments()
    skoleintra.pgWeekplans.skoleWeekplans()

klAll, lektierAll = skoleintra.pgLektier.getLektieLister()

errCode = skoleintra.pgLektieSender.sendEmailSms(klAll, lektierAll)
sys.exit(errCode)
