Forældreintra til Email
=======================

ForældreIntra er en del af SkoleIntra, der brugers af næsten alle
danske folkeskoler til kommunikation mellem skole og hjem. fskintra
logger på ForældreIntra og konverterer indholdet til almindelige
emails. Du vil bl.a. modtage en email, hver gang der kommer nyt et af
flg. steder:

* Forsiden: Nyheder på opslagstavlen
* Forsiden: Nyt forside billede, skema, osv.
* Dialog/beskeder: Nye beskeder (både sendt og modtaget)
* Arkiv/dokumenter: Nye dokumenter
* Ugeplaner: Nye ugeplaner
* Lektier: Speciel på forskellige emailadresser samt SMS (kan bruges til hele klasser)

Alle emails bliver gemt, dvs. du får kun en email, såfremt der faktisk
er kommet nyt.

Eksempel
========

Som standard tilbyde ForældreIntra at sende dig en email hvis der er
nye beskeder eller andet, men du får kun overskriften/første linje af
beskeden - nogle gange endda kun, hvem der har skrevet den:

<pre>
> Advisering om nyt i ForældreIntra - Dinoskolen:
>
> 3.a:
> *Besked*    Besked fra Peter Nielsen
>
> Klik for at åbne ForældreIntra eller MobilIntra.
</pre>

Med fskintra får du i stedet en email med selve indholdet af beskeden
og behøver ikke længere at logge på, for at se, hvad der står

<pre>
> Hvor er Annas sorte højregummistøvle?
>
> Fra: Peter Nielsen (Anna 3.a)
> Til: Anders Andersen (Bjarke 3.a), m.fl.
> Dato: 07-09-2013 12:14:16
>
> Anna kan ikke finde sin ene sorte gummistøvle - og får nu våde fødder.
>
> Kan du finde den? Vi/Anna giver en lakrids, hvis den bliver fundet og bragt til hende i 3.a
>
> Mvh, Peter Nielsen
</pre>

Krav
====

* Linux, FreeBSD (Virker måske i Windows, men det er ikke afprøvet)
* Python 2.5+ (ikke 3.x)
* Pythonpakker: mechanize (0.2.5), BeautifulSoup (3.2.x)

Du kan få de krævede pythonpakker i Ubuntu ved at køre

    sudo apt-get install python-beautifulsoup python-mechanize

Pakkerne i standard Ubuntu 12.04 virker.
Alternativt kan du bruge easy_install

    sudo easy_install beautifulsoup mechanize


HOWTO
=====

Opsætning
---------

Hent de krævede pythonpakker (se ovenfor). Dernæst hentes nyeste
version af programmet fra nedenstående side - fx ved at hente
zip-filen, eller endnu bedre ved at bruge git

    https://github.com/svalgaard/fskintra

Kør følgende kommando, og besvar spørgsmålene

    fskintra.py --config

Til slut testes programmet ved at køre det

    fskintra.py --sms navn

Din opsætning gemmes i $HOME/.skoleintra/skoleintra.txt. Såfremt du
kun skal rette lidt kan det evt. være smartest at rette direkte i
filen i stedet for at køre --config igen.

I $HOME/.skoleintra gemmes også alt hentet indhold og alle sendte
emails.

Opsætning til lektie Email/SMS
------------------------------

Ønskes info om lektier, skal dette opsættes manuelt efter ovenstående
konfiguration.

i configurationsfilen, ~/.skoleintra/skoleintra.txt:
Indsæt linier:
    # Sti til sqlite3 database (filen laves automatisk af fskintra.py)
    lektiedb=~/.skoleintra/lektier.db
    lektieids=[1, 2, 3]
hvor tallene er ID=<num> for din(e) barn/børn i url'en for Lektier.

Ønskes SMS med info om lektier, skal der oprettes en sektion som denne
for hver barn/gruppe der skal have en SMS.

Dette er tiltænkt at barn/børn kan få en SMS efter skoletid med
lektier og forældre kan få en email.

Der skal laves en smsgw-gruppe, se [smsgw-xxx] eksemplet herunder.

Desuden skal der laves en [sms-navn] seksion for hver klasse (et eller
flere børn/forældre)

- navn: [sms-<navn>] <navn> erstattes med navnet på sms-gruppen.
- gw: SMS gateway, pt. kun understøttelse for smsit.dk og
  android app
  (https://play.google.com/store/apps/details?id=eu.apksoft.android.smsgateway)
- lektieid: Er id - se lektieids ovenfor
- days: Antal skoledage der skal sendes lektier for
- min_msgs_days: Minimum antal dage med lektier der skal sendes for
  (hvis der ikke er lektier til hver dag)

- from: Tekst der angiver afsender (max 11 bgstaver, nogle
  telefoner/udbydere fjerner mellemrum)

  Bruges kun for nogle SMS Gateways (ikke for afsendelse fra SMS
  kort/alm. tlf. abonnement, men for smsit.dk
- to: Liste med Modtagere, emailadresser og mobilnr.
  nr. +45 bliver automatisk sat foran (hvis krævet), og må ikke være
  inkluderet her.

Skal der sendes SMS/email til flere klasser skal der oprettes flere
[sms-navnXX] grupper.

Alle emails sendes som een email, pt. sendes til Bcc adresser, men
dette kan blive ændret uden varsel.

For at sende en SMS oprettes der er cronjob, der kalder
"/sti/til/fskintra.py --sms navn", og kører som dig, eller en anden
bruger der har ~/.skoleintra/skoleintra.txt.

Skal der sendes sms til flere sms-grupper samtidig, ændres til
"--sms navn1,navn2" (uden mellemrum imellem de forskellige sms-grupper).

    [smsgw-xxx]
    # Supported gw's:
    # sms_gw=smsit.dk
    #    needs sms_key=<password key>
    # sms_gw=eu.apksoft.android.smsgateway
    #    needs sms_key=<password> (not tested without)
    #    See https://play.google.com/store/apps/details?id=eu.apksoft.android.smsgateway
    # Ex.:
    [smsgw-smsit.dk]
    gw=smsit.dk
    key=YourCodeFromSmsit.dk
    url=DummyNotNeeded

    [smsgw-1]
    gw=eu.apksoft.android.smsgateway
    url=http://1.2.3.4:9090/sendsms
    key=MyPassWord

    [sms-navn]
    gw=smsgw-1
    lektieid=1
    days=1
    min_msgs_days=1
    from=Lektier
    to=
    	# Peter
	Peter Pedersen <peter@example.org>
	12345678
	# Peters forældre
	hjemme_v_peter@example.org
	# Søren
	soren@example.org

Cron-job
--------

Tilføj flg. linje til din crontab fil for at få programmet til at køre
to gange dagligt:

    PYTHONIOENCODING=UTF-8
    25 6,18 * * * /path/to/fskintra.py -q

Ved at tilføje -q, får du kun en email, såfremt der er noget
interessant at se (og ikke en email om, at fskintra har prøvet at
finde noget nyt uden at gøre det).

Linjen med PYTHONIOENCODING=UTF-8 er ikke altid nødvendig (se evt. nedenfor),
men er næsten altid en god idé.

Problemer?
----------

**UnicodeEncodeError**
I nogle situationer giver Python desværre en unicode-fejl lignende følgende

    Traceback (most recent call last):
      File "/home/user/fsk/fskintra.py", line 12, in <module>
        cnames = skoleintra.schildren.skoleGetChildren()
      File "/home/user/fsk/skoleintra/schildren.py", line 22, in skoleGetChildren
        config.log(u'Henter liste af bM-CM-8rn')
      File "/home/user/fsk/skoleintra/config.py", line 185, in log
        sys.stderr.write(u'%s\n' % s)
    UnicodeEncodeError: 'ascii' codec can't encode character u'\xf8' in position 17: ordinal not in range(128)

En løsning vil i næsten alle tilfælde være at sætte miljøvariablen PYTHONIOENCODING til UTF-8.

Hvis du bruger bash eller lignende (hvis du ikke ved, om du gør, så gør
du sikkert).

    export PYTHONIOENCODING=UTF-8
    /sti/til/fskintra

Hvis du bruger tcsh eller lignende:

    setenv PYTHONIOENCODING UTF-8
    /sti/til/fskintra

**HTTP/HTML fejl**
Den nuværende version af fskintra er ikke altid god til at håndtere
http/html fejl. Hvis der sker en fejl, kan du for det meste løse
problemet ved at køre fskintra igen. Hvis det ikke er nok, kan du
evt. tilføje parameteren -v for muligvis at se mere om, hvad der går
galt:

    fskintra.py -v

Du er evt. også velkommen til at kontakte mig. Såfremt det ikke
virker, må du meget gerne vedhæfte hvad der bliver skrevet, når
fskintra.py køres med -v.

Lektie Email/SMS
================

Lektie Email/SMS er en ekstra feature, som sender Email/SMS med lektier.

Denne funktion kan bruges til at sende email/SMS til flere forældre og
elever fra flere forskellige klasser.

Opsætningen inkluderer ikke dette, og skal gøres direkte i
konfigurationsfilen, se ovenfor.

Lektie SMS format
-----------------

Lektie SMS er lidt kompakt, både for at spare på antal SMS'er og for
at få mindre fyld på en lille skærm.

Eks. (normalt vil man nok ikke få SMS om lektier for så lang tid):

    Mat: Matematiklektier til i morgen
    Dan: Dansk til i morgen
    F:
    Eng: Engelsk lektier til fredag
    M1:
    Dan: Dansk til mandag i næste uge
    M2:
    Dan: Dansk til mandag om 2 uger

Forklaring:

Lektier til imorgen står uden ugedag, men med fagets navn (ofte
forkortet), med eet fag pr. linie.

Ved skift til ny ugedag står der 1-2 bogstavsforkotelse for ugedagen
(M, Ti, O, To, F, L, S) og hvis det er en uge frem står der et 1-tal
bagefter, 2 uger frem et 2-tal osv. og : samt ny linie.

Lektie Web
==========

Indholdet er det samme som for Lektie Email/SMS, men her vises
indholdet fra databasen over lektier.

Dette bør kun stilles tilrådighed for andre efter aftale med den
dataansvarlige (skolelederen).

Funktionaliteten kan bruges til at hente lektier for flere klasser og
vises samlet for hver enkelt dag.

Folderen www kopieres til en webserver folder, som kan eksekvere
python kode (f. eks. cgi-bin). Hvis det skal bruges fra smartphones,
er det lettest at undgå passwords, men have en url der er lang og med
tilfældige karakterer + bede søgemaskiner om at ignorere det
vha. robots.txt. Selvfølgelig skal der ikke være links til dette fra
andre websites.

Husk at rename filen lektier til noget med en række tilfældige karakterer!

I kopien af www-folderen skal der laves et symlink til lektie.db filen.

I roden af webserveren bør der placeres en favicon.ico - den bliver
refereret i de genererede html sider.

P.t. vil links skrevet i lektier være aktive, og vil kunne ses i logs
som referrer hvis disse benyttes! F. eks vil smilies indsat via
lærenes editor referere til skolens intra.

Hvem?
=====

fskintra er skrevet/opdateres af
Jens Svalgaard kohrt - http://svalgaard.net/jens/ - github AT svalgaard.net

Ændringer og forslag er bl.a. kommet fra
* Jacob Kjeldahl, https://github.com/kjeldahl
* Michael Legart, https://github.com/legart
* Jesper Rønn-Jensen, https://github.com/jesperronn
* Benny Simonsen, https://github.com/bennyslbs
