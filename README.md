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

## Initiales Setup Frontend

Nach Ausführung obiger Schritte wird zur Frontendentwicklung ein weiteres Toolset benötigt.

### Was Du brauchst

- [node](http://nodejs.org/)
- [grunt](http://gruntjs.com/)

Die Installation von `node.js` ist sehr systemspezifisch. Am *einfachsten* kann man `node.js` von der Website installieren, sauberer allerdings und deswegen empfohlen ist die Installation mit [homebrew](http://brew.sh/).

Wenn node installiert ist, zuerst das Grunt-Commandline-Interface installieren:

	cd ~
	npm install -g grunt-cli

Dann eine lokale Kopie von grunt anlegen im Projektverzeichnis:

	cd friedbert
	npm install grunt --save-dev

Dadurch werden ein Verzeichnis `node_modules` angelegt. Dies bitte nicht anfassen.









