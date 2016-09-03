Forældreintra lektier til Web/Email/SMS
=======================================

Dette er kun en beskrivelse af lektiedelen. Generel beskrivelse kan ses i [README.md](README.md).

Lektiedelen kan bruges til at vise lektiebøger fra Forældreintra på en overskuelig måde:
* På website for een eller flere klasser
* På email for een klasse pr. email
* På SMS for de nærmeste dage (korte men læsbare SMS'er)

Lektie Web
==========

Indholdet er det samme som for Lektie Email/SMS, men her vises
indholdet fra databasen over lektier.

Dette bør kun stilles tilrådighed for andre efter aftale med den
dataansvarlige (skolelederen).

Funktionaliteten kan bruges til at hente lektier for flere klasser og
vises samlet for hver enkelt dag.

Links i lektier vil blive lavet korrupte idet :// erstattes af
CORRUPURL://, og httpCORRUPURL:// håndterer browsere (forhåbntlig)
ikke. Dette er for ikke at få referencer til lektie-websiden på andre
web-servere, hvis der ikke bruges password.

[Eksempel](http://slbs.dk/skfi/lektieweb_ex.html) eller 
[lektieweb_ex.html (skal først gemmes lokalt; favicons virker ikke i eksmplet, så der mangler et ikon hvis du bookmarker)](lektieweb_ex.html).

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

HOWTO
=====

Opsætning
---------

Ønskes info om lektier, skal dette opsættes manuelt efter konfiguration som omtalt i [README.md](README.md) er lavet.

I configurationsfilen, ~/.skoleintra/skoleintra.txt:
Indsæt linier:
    # Sti til sqlite3 database (filen laves automatisk af fskintra.py)
    lektiedb=~/.skoleintra/lektier.db
    lektieids=[1, 2, 3]
hvor tallene er ID=<num> for din(e) barn/børn i url'en for Lektier.

Desuden kan der indsættes skip-normal=<anything> i [default]
sektionen, og fskintra's normale brug til alt andet end
LektieWeb/Mail/SMS er disablet (overruler --skip-normal).  Dette kan
bruges hvis man ønsker at bruge en separat skoleintra.txt af fskintra kun til lektier.

Tilsvarende kan der indsættes skip-normal=<anything> i [default]
sektionen, og LektieWeb/Mail/SMS delen er deaktiveret.

Ønskes Email eller SMS med info om lektier, skal der oprettes en sektion som denne
for hver barn/gruppe der skal have en Email eller SMS.

Dette er tiltænkt at barn/børn kan få en SMS efter skoletid med
lektier og forældre kan få en email.

Der skal laves en smsgw-gruppe for hver gw=xxx is sms-grupperne, se
[smsgw-xxx] eksemplet herunder.

Desuden skal der laves en [sms-navn] seksion for hver klasse (et eller
flere børn/forældre)

- navn: [sms-<navn>] <navn> erstattes med navnet på sms-gruppen.
- gw: SMS gateway,
  Pt. kun understøttelse for:
  - NoSMSGW (disable afsendelse af SMS for gruppen) - Kræver ingen smsgw
  - smsgw - https://github.com/bennyslbs/smsgw (git submodul til fskintra i branchen lektier
  - smsit.dk
  - android app https://play.google.com/store/apps/details?id=eu.apksoft.android.smsgateway
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
    # sms gw=gw=NoSMSGW
    #    needs: No parameters
    # sms gw=smsgw
    #    needs:
    #    - host (host where smsgwd is running, host at server must be "like" this, e.g localhost->localhost)
    #    - port Which port is smsgwd listening on (default 2525)
    #    - priority (set to high number, e.g 20 (0 is highest priority))
    #    - smsgwgw gw in smsgw, just use the cheap on or any to make higher security that an GW is working
    #    - from Sender name/number (only works for some gw's (e.g. smsit.dk)
    #    - GetDeliveryReport = True if delivery report should be checked, else False
    #    - verbose, not used for now
    # sms gw=smsit.dk
    #    needs sms_key=<password key>, url=<dummy>
    # sms gw=eu.apksoft.android.smsgateway
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

Til slut testes programmet ved at køre det

    fskintra.py --sms navn1,navn2

Cron-job
--------

Se [README.md](README.md), tilføj et cronjob med `--sms` for at få
sendt SMSer eller emails med lektier.

Det er smartest kun at køre `fskintra.py --sms navnXX` een gang hver
dag, og kun mandag til fredag (idet det er sjældent at der kommer nye
lektier i weekenden).

LektieSMS og LektieEmail sendes også selvom der ikke er sket ændringer.

    # Fri kl. 12:55 - send SMS 15 min. efter fri
    10 13	* * 1 /path/to/fskintra.py -q --sms 0kl,1kl,2kl,3kl,,,,,,,,,6kl,7kl
    10 13	* * 2 /path/to/fskintra.py -q --sms 0kl,1kl,2kl,3kl
    10 13	* * 3 /path/to/fskintra.py -q --sms 0kl,1kl,2kl,3kl,4kl,5kl,6kl,7kl
    10 13	* * 4 /path/to/fskintra.py -q --sms 0kl,1kl,2kl,3kl,4kl
    10 13	* * 5 /path/to/fskintra.py -q --sms 0kl,1kl,2kl,3kl,4kl,5kl
    # Fri kl. 13:40 - send SMS 15 min. efter fri
    ...

Det kan være en fordel at køre cron-jobbet efter lærerne har opdateret
klassens lektier og inden det er tid til at lave lektier.

Opsætning af webserver til LektieWeb
------------------------------------

For at få gemt lektier i databasen skal fskintra køres f. eks. fra
cron, hvor lektiedb og lektieids er opsat. Se Opsætning til lektie
Email/SMS.

Lektie Web viser udelukkende indhold fra databasen, men læser ikke
konfiguationsfilen skoleintra.txt.

I en webserver folder, som kan eksekvere python kode
(f. eks. cgi-bin) laves der symlink til <fskintra>/www/lektier. Det
skal være et symlink. Hvis det er en kopi, skal der ændres i kopien -
se hjælp i filen.

Hvis det skal bruges fra smartphones, er det lettest at undgå
passwords, men have en url der er lang og med tilfældige karakterer +
bede søgemaskiner om at ignorere det vha. robots.txt. Selvfølgelig
skal der ikke være links til dette fra andre websites.

Er der ikke password, husk da at rename filen lektier til noget med en
række tilfældige karakterer!

Der skal laves et symlink til lektie.db filen. sym-linket skal ligge
samme sted og have samme navn som symlinket til python scriptet
lekter, dog tilføjet endelsen .db. Hvis python-script linket hedder
/var/www/cgi-bin/lektier.py, skal lektier.db linket hedde
/var/www/cgi-bin/lektier.py.db.

I roden af webserveren bør der ligeledes laves et symlink til eller
kopi af www/root/fskintra. Der ligger favicons mm. fra
http://realfavicongenerator.net/ og en enkelt smily som bruges istedet
for alle skoleintra editor-smilies.

Ekstra opsætning i <site>.conf apache konfigurationsfilen, som antager:
- LektieWeb kan tilgås via =http(s)://eksempel.dk/<uniq string where LektieWeb is located>/lektier=
- Folderen =/somewhere/outside/apache/webpages/= indeholder:
  - `lektier    -> /home/<fskuser>/git/github.com/bennyslbs/fskintra/www/lektier`
  - `lektier.db -> /home/<fskuser>/.skoleintra/lektier.db`
  - `urlf       -> /home/<fskuser>/git/github.com/bennyslbs/fskintra/www/urlf`

- Hvor:
  - `<fskuser>` er brugeren som kører fskintra.
  - `/home/<fskuser>/git/github.com/bennyslbs/fskintra` er roden af git-repositoriet, husk det skal være branchen `lektier`.

```
        ScriptAlias /<uniq string where LektieWeb is located>/somewhere/outside/apache/webpages/
        # /urlf points to urlf in the hidden dir, but is not hidden;
        # Purpose: used to fetch a url from the hidden url via unhidden url
        ScriptAlias /urlf /somewhere/outside/apache/webpages/urlf
        <Directory /var/www/fskintra.slbs.dk-cgi.hidden>
            Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
            Order allow,deny
            Allow from all
            SetHandler cgi-script
        </Directory>
```

TODO ved nyt skoleår
===============================

* Opdater klasser i config fil
.* Tilføj nye klasser og fjern gamle klasser fra `lektieids=[...]`

   Note: Skolens medarbejdere skal manuelt ændre klassens navne i
   lektierbøgerne i skoleintra, samt oprette lektiebøger for nye klasser,
   så dette vil ikke nødvendigvis være ændret før skolestart.
.* Inkrementer klasser i sms gruppenavnene `[sms-Xkl]`
* Opdater hvornår klasserne har fri i `/etc/crontab`
* Fjern gamle klasser fra classes tabellen i `lekter.db`:

    sqlite3 ~/.skoleintra/lektier.db
    sqlite> select * from classes;
    <list of ID and Class name are shown>
    sqlite> delete from classes where id=<ID>;
* Check at alt ser ok ud: gå ind på Lektieweb, og tilføj f. eks `&kl=all` eller `&kl=[id0, id1, ...]` til urlen (overruler `&klX=`)
