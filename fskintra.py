#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# Normal messages
if not skoleintra.config.skip_normal:
    for cname in cnames:
        skoleintra.schildren.skoleSelectChild(cname)

        skoleintra.pgContactLists.skoleContactLists()
        skoleintra.pgFrontpage.skoleFrontpage()
        skoleintra.pgDialogue.skoleDialogue()
        skoleintra.pgDocuments.skoleDocuments()
        skoleintra.pgWeekplans.skoleWeekplans()

# Lektier
if not skoleintra.config.skip_lektier:
    klAll, lektierAll = skoleintra.pgLektier.getLektieLister()
    skoleintra.pgLektieSender.sendEmailSms(klAll, lektierAll)
