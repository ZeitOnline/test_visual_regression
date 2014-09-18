# -*- coding: utf-8 -*-
import re

import mock
import pyramid.threadlocal
import pyramid.config
import lxml

#macro testing


def test_macro_main_nav_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/layout_macro.tpl')
    lines = tpl.module.main_nav().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    wrapper = '<nav class="main_nav_new">'
    logo_image = '<div class="logo_bar__image">'
    logo_menue = '<div class="logo_bar__menue">'
    teaser = '<div class="main_nav__teaser">'
    community = '<div class="main_nav__community" data-dropdown="true">'
    ressorts = '<div class="main_nav__ressorts" data-dropdown="true">'
    services = '<div class="main_nav__services" data-dropdown="true">'
    classifieds = '<div class="main_nav__classifieds" data-dropdown="true">'
    search = '<div class="main_nav__search" data-dropdown="true">'
    tags = '<div class="main_nav__tags">'
    assert wrapper in output
    assert logo_image in output
    assert logo_menue in output
    assert teaser in output
    assert community in output
    assert ressorts in output
    assert services in output
    assert classifieds in output
    assert search in output
    assert tags in output


def test_macro_main_nav_services_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/layout_macro.tpl')
    lines = tpl.module.main_nav_services().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    abo = '<li><a href="http://www.zeitabo.de/?mcwt=2009_07_0002"' \
        ' id="hp.global.topnav.links.abo">Abo</a></li>'
    shop = '<li><a href="http://shop.zeit.de?et=l6VVNm&amp;et_cid=42&amp;' \
        'et_lid=175&amp;et_sub=Startseite_header"' \
        ' id="hp.global.topnav.links.shop">Shop</a></li>'
    epaper = '<li><a href="https://premium.zeit.de/?' \
        'wt_mc=pm.intern.fix.zeitde.fix.dach.text.epaper"' \
        ' id="hp.global.topnav.links.epaper">E-Paper</a></li>'
    audio = '<li><a href="https://premium.zeit.de/abo/digitalpaket5' \
        '?wt_mc=pm.intern.fix.zeitde.fix.dach.text.audio"' \
        ' id="hp.global.topnav.links.audio">Audio</a></li>'
    apps = '<li><a href="https://premium.zeit.de/abo/appsios?' \
        'wt_mc=pm.intern.fix.zeitde.fix.dach.text.apps"' \
        ' id="hp.global.topnav.links.apps">Apps</a></li>'
    archiv = '<li><a href="http://www.zeit.de/archiv"' \
        ' id="hp.global.topnav.links.archiv">Archiv</a></li>'
    assert abo in output
    assert shop in output
    assert epaper in output
    assert audio in output
    assert apps in output
    assert archiv in output


def test_macro_main_nav_classifieds_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/layout_macro.tpl')
    lines = tpl.module.main_nav_classifieds().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    jobs = '<li><a href="http://jobs.zeit.de/"' \
        ' id="hp.global.topnav.links.jobs">Jobs</a></li>'
    psuche = '<li><a href="http://www.zeit.de/angebote/partnersuche/index?' \
        'pscode=01_100_20003_0001_0001_0005_empty_AF00ID_GV00ID"' \
        ' id="hp.global.topnav.links.partnersuche">Partnersuche</a></li>'
    more = '<li class="main_nav__classifieds__more">'
    immo = '<li><a href="http://zeit.immowelt.de/" rel="nofollow"' \
        ' id="hp.global.topnav.links.immobilien">Immobilien</a></li>'
    markt = '<li><a href="http://automarkt.zeit.de/"' \
        ' id="hp.global.topnav.links.automarkt">Automarkt</a></li>'
    assert jobs in output
    assert psuche in output
    assert more in output
    assert immo in output
    assert markt in output


def test_macro_main_nav_community_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/layout_macro.tpl')
    lines = tpl.module.main_nav_community().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    link = '<a href="http://community.zeit.de/user/login?' \
        'destination=http://www.zeit.de/index"' \
        ' rel="nofollow" class="user" id="drupal_login">'
    logo = '<span class="main_nav__community__image' \
        ' icon-zon-logo-navigation_login"></span>'
    text = 'Anmelden'
    assert link in output
    assert logo in output
    assert text in output


def test_macro_main_nav_logo_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/layout_macro.tpl')
    lines = tpl.module.main_nav_logo().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    link = '<a href="http://www.zeit.de/index"' \
        ' title="Nachrichten auf ZEIT ONLINE"' \
        ' class="icon-zon-logo-desktop" ' \
        'id="hp.global.topnav.centerpages.logo">'
    assert link in output


def test_macro_main_nav_burger_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/layout_macro.tpl')
    lines = tpl.module.main_nav_burger().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    link = '<a href="#">'
    logo = '<div class="logo_bar__menue__image' \
        ' main_nav__icon--plain ' \
        'icon-zon-logo-navigation_menu"></div>'
    logo_hover = '<div class="logo_bar__menue__image' \
        ' main_nav__icon--hover' \
        ' icon-zon-logo-navigation_menu-hover"></div>'
    assert link in output
    assert logo in output
    assert logo_hover in output


def test_macro_main_nav_search_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/layout_macro.tpl')
    lines = tpl.module.main_nav_search().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    form = '<form accept-charset="utf-8" method="get"' \
        ' class="search" role="search" ' \
        'action="http://www.zeit.de/suche/index">'
    label = '<label for="q" class="hideme">suchen</label>'
    button = '<button class="search__button"' \
        ' type="submit" tabindex="2">'
    icon = '<span class="icon-zon-logo-navigation_suche' \
        ' search__button__image main_nav__icon--plain"></span>'
    icon_hover = '<span class="icon-zon-logo-navigation_suche-hover' \
        ' search__button__image main_nav__icon--hover"></span>'
    input_box = '<input class="search__input" id="q" name="q"' \
        ' type="search" placeholder="Suche" tabindex="1">'
    button_close = '<button class="search__close"' \
        ' type="submit" tabindex="2">'
    icon_close = '<span class="icon-zon-logo-navigation_close-small' \
        ' search__close__image"></span>'
    assert form in output
    assert label in output
    assert button in output
    assert icon in output
    assert icon_hover in output
    assert input_box in output
    assert button_close in output
    assert icon_close in output


def test_macro_main_nav_ressorts_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/layout_macro.tpl')
    lines = tpl.module.main_nav_ressorts().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    markup = '<nav role="navigation"><ul class="primary-nav">' \
        '<li class="primary-nav__item"><a class="primary-nav__link" ' \
        'href="#">Politik</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link primary-nav__link--current" ' \
        'href="#">Gesellschaft</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link" href="#">Wirtschaft</a>' \
        '</li><li class="primary-nav__item"><a class="primary-nav__link" ' \
        'href="#">Kultur</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link" href="#">Wissen</a>' \
        '</li><li class="primary-nav__item"><a class="primary-nav__link"' \
        ' href="#">Digital</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link" href="#">Studium</a></li>' \
        '<li class="primary-nav__item"><a class="primary-nav__link"' \
        ' href="#">Karriere</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link" href="#">Reise</a></li>' \
        '<li class="primary-nav__item"><a class="primary-nav__link"' \
        ' href="#">Sport</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link" href="#">Spiele</a></li></ul></nav>'
    assert markup == output


def test_macro_main_nav_tags_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/layout_macro.tpl')
    lines = tpl.module.main_nav_tags().splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    title = '<span class="main_nav__tags__label">Schwerpunkte'
    ul_list = '<ul>'
    assert title in output
    assert ul_list in output


def test_macro_main_nav_date_produce_markup(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/macros/layout_macro.tpl')
    lines = tpl.module.main_nav_date('Mein Datum').splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    date = 'Mein Datum'
    assert date == output


#integration testing

def test_article_has_valid_main_nav_structure(testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    lines = browser.contents.splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert '<nav class="main_nav_new">' in output
    assert '<div class="logo_bar__image">' in output
    assert '<div class="logo_bar__menue">' in output
    assert '<div class="main_nav__teaser">' in output
    assert '<div class="main_nav__community"' \
        ' data-dropdown="true">' in output
    assert '<div class="main_nav__ressorts"' \
        ' data-dropdown="true">' in output
    assert '<div class="main_nav__services"' \
        ' data-dropdown="true">' in output
    assert '<div class="main_nav__classifieds"' \
        ' data-dropdown="true">' in output
    assert '<div class="main_nav__search"' \
        ' data-dropdown="true">' in output
    assert '<div class="main_nav__tags">' in output


def test_article_has_valid_services_structure(testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    lines = browser.contents.splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert 'id="hp.global.topnav.links.abo">Abo</a>' in output
    assert 'id="hp.global.topnav.links.shop">Shop</a>' in output
    assert 'id="hp.global.topnav.links.epaper">E-Paper</a>' in output
    assert 'id="hp.global.topnav.links.audio">Audio</a>' in output
    assert 'id="hp.global.topnav.links.apps">Apps</a>' in output
    assert 'id="hp.global.topnav.links.archiv">Archiv</a>' in output


def test_article_has_valid_classifieds_structure(testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    lines = browser.contents.splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert 'id="hp.global.topnav.links.jobs">Jobs</a>' in output
    assert 'id="hp.global.topnav.links.partnersuche">' \
        'Partnersuche</a>' in output
    assert 'id="hp.global.topnav.links.immobilien">Immobilien</a>' in output
    assert 'id="hp.global.topnav.links.automarkt">Automarkt</a>' in output


def test_article_has_valid_community_structure(testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    lines = browser.contents.splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert '<a href="http://community.zeit.de/user/login?' in output
    assert '<span class="main_nav__community__image' in output
    assert 'Anmelden' in output


def test_article_has_valid_logo_structure(testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    lines = browser.contents.splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert '<a href="http://www.zeit.de/index"' \
        ' title="Nachrichten auf ZEIT ONLINE"' \
        ' class="icon-zon-logo-desktop" ' \
        'id="hp.global.topnav.centerpages.logo">' in output


def test_article_has_valid_burger_structure(testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    lines = browser.contents.splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert '<div class="logo_bar__menue__image' \
        ' main_nav__icon--plain ' \
        'icon-zon-logo-navigation_menu"></div>' in output
    assert '<div class="logo_bar__menue__image' \
        ' main_nav__icon--hover' \
        ' icon-zon-logo-navigation_menu-hover"></div>' in output


def test_article_has_valid_burger_structure(testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    lines = browser.contents.splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    assert '<div class="logo_bar__menue__image' \
        ' main_nav__icon--plain ' \
        'icon-zon-logo-navigation_menu"></div>' in output
    assert '<div class="logo_bar__menue__image' \
        ' main_nav__icon--hover' \
        ' icon-zon-logo-navigation_menu-hover"></div>' in output


def test_article_has_valid_search_structure(testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    lines = browser.contents.splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    form = '<form accept-charset="utf-8" method="get"' \
        ' class="search" role="search" ' \
        'action="http://www.zeit.de/suche/index">'
    label = '<label for="q" class="hideme">suchen</label>'
    button = '<button class="search__button"' \
        ' type="submit" tabindex="2">'
    icon = '<span class="icon-zon-logo-navigation_suche' \
        ' search__button__image main_nav__icon--plain"></span>'
    icon_hover = '<span class="icon-zon-logo-navigation_suche-hover' \
        ' search__button__image main_nav__icon--hover"></span>'
    input_box = '<input class="search__input" id="q" name="q"' \
        ' type="search" placeholder="Suche" tabindex="1">'
    button_close = '<button class="search__close"' \
        ' type="submit" tabindex="2">'
    icon_close = '<span class="icon-zon-logo-navigation_close-small' \
        ' search__close__image"></span>'
    assert form in output
    assert label in output
    assert button in output
    assert icon in output
    assert icon_hover in output
    assert input_box in output
    assert button_close in output
    assert icon_close in output


def test_article_has_valid_ressort_structure(testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    lines = browser.contents.splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    markup = '<nav role="navigation"><ul class="primary-nav">' \
        '<li class="primary-nav__item"><a class="primary-nav__link" ' \
        'href="#">Politik</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link primary-nav__link--current" ' \
        'href="#">Gesellschaft</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link" href="#">Wirtschaft</a>' \
        '</li><li class="primary-nav__item"><a class="primary-nav__link" ' \
        'href="#">Kultur</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link" href="#">Wissen</a>' \
        '</li><li class="primary-nav__item"><a class="primary-nav__link"' \
        ' href="#">Digital</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link" href="#">Studium</a></li>' \
        '<li class="primary-nav__item"><a class="primary-nav__link"' \
        ' href="#">Karriere</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link" href="#">Reise</a></li>' \
        '<li class="primary-nav__item"><a class="primary-nav__link"' \
        ' href="#">Sport</a></li><li class="primary-nav__item">' \
        '<a class="primary-nav__link" href="#">Spiele</a></li></ul></nav>'
    assert markup in output


def test_article_has_valid_tag_structure(testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    lines = browser.contents.splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    title = '<span class="main_nav__tags__label">Schwerpunkte'
    ul_list = '<ul>'
    assert title in output
    assert ul_list in output


def test_article_has_valid_nav_date_structure(testserver, testbrowser):
    browser = testbrowser('%s/zeit-magazin/index' % testserver.url)
    lines = browser.contents.splitlines()
    output = ""
    for line in lines:
        output += line.strip()
    date = '3. September 2014 10:50 Uhr'
    assert date in output

#selenium test resizing
