Zeit Web Project
================

## Initiales Setup Pyramid-App

Zunächst das Repository clonen

	git clone git@github.com:ZeitOnline/zeit.web

Ins Verzeichnis wechseln

    cd zeit.web

Per virtualenv die evtl. Systemabhängigkeiten ausknipsen

    virtualenv --no-site-packages .

Setup ausführen als development

    bin/python setup.py develop

## App starten

Nach folgendem Aufruf lauscht die App auf Port 9090

    bin/pserve web.ini

Folgende URL liefert eine erste Sicht auf einen Artikel

    http://localhost:9090/artikel/01

Die Option `--reload` sorgt dafür, dass bei editiertem Code der Server neu gestartet wird

	bin/pserve web.ini --reload

## Initiales Setup

Nach Ausführung obiger Schritte wird zur Entwicklung ein weiteres Toolset benötigt, bestehend aus:

- [node](http://nodejs.org/)
- [grunt](http://gruntjs.com/)

Die Installation von `node.js` ist sehr systemspezifisch. Am *einfachsten* kann man `node.js` von der Website installieren, sauberer allerdings und deswegen empfohlen ist die Installation mit [homebrew](http://brew.sh/).

Wenn node installiert ist, zuerst das Grunt-Commandline-Interface installieren:

    cd ~
    npm install -g grunt-cli

Dann eine lokale Kopie von grunt anlegen im Projektverzeichnis:

    cd zeit.web
    npm install grunt --save-dev

Dadurch werden ein Verzeichnis `node_modules` angelegt. Dies bitte nicht anfassen. Werden neue Grunt-Module dem Projekt hinzugefügt, müssen diese ggf. lokal nachinstalliert werden, da die Module nicht ins Repository eingecheckt werden:

    npm install [grunt-module-name] --save-dev

`--save-dev` sorgt dafür, dass das Modul in die package.json aufgenommen wird.

Konfigurationsänderungen und -updates sind durch das Anpassen der package.json, vor allem aber der Gruntfile.js umzusetzen.

Ist alles fertig installiert, kann mit diesem Kommando der Grunt Watchdemon gestartet werden

    grunt watch
