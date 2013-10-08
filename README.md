ZMO on Friedbert
================

## Initiales Setup Pyramid-App

Zunächst Repo clonen

	git clone git@github.com:ZeitOnline/friedbert

Ins Verzeichnis wechseln

    cd friedbert

Per virtualenv die evtl. Systemabhängigkeiten ausknipsen

    virtualenv --no-site-packages .

Pyramid installieren

    bin/easy_install pyramid

Setup ausführen als development

    bin/python setup.py develop

Waitress (Webserver) installieren

    bin/pip install waitress

## App starten

Nach folgendem Aufruf lauscht die App auf Port 9090

    bin/pserve frontend.ini

Folgende URL liefert eine erste Sicht auf einen Artikel

    http://localhost:9090/politik/deutschland/2013-07/wahlbeobachter-portraets 

Die Option --reload sorgt dafür, dass bei editiertem Code der Server neu gestartet wird

	bin/pserve frontend.ini --reload



