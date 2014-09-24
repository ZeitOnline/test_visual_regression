# -*- coding: utf-8 -*-
import re

import mock
import pyramid.threadlocal
import pyramid.config
import lxml

#macro testing


def test_nav_markup_should_match_css_selectors(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.render()
    html = lxml.html.fromstring(html_str).cssselect
    assert len(html('nav.main_nav')) == 1,\
        'just one .main_nav should be present'

    assert len(html('nav.main_nav > div')) == 9,\
        'nine divs within .main_nav'

    assert '</div><div class="main_nav__date"' in html_str,\
        'don\'t break line here, due to inline-block state'

    assert len(html('nav.main_nav > div.logo_bar >'
        'div.logo_bar__image')) == 1, 'just one .logo_bar__image'

    assert len(html('nav.main_nav > div.logo_bar >'
        'div.logo_bar__menue')) == 1, 'just one .logo_bar__menue'

    assert len(html('nav.main_nav > div.main_nav__teaser')) == 1,\
        'just one .main_nav__teaser'

    assert len(html('nav.main_nav > div.main_nav__community'
        '[data-dropdown="true"]')) == 1,\
        'just one .main_nav__community w/ data-dropdown=true'

    assert len(html('nav.main_nav > div.main_nav__ressorts'
        '[data-dropdown="true"]')) == 1,\
        'just one .main_nav__ressorts w/ data-dropdown=true'

    assert len(html('nav.main_nav > div.main_nav__services'
        '[data-dropdown="true"]')) == 1,\
        'just one .main_nav__services w/ data-dropdown=true'

    assert len(html('nav.main_nav > div.main_nav__classifieds'
        '[data-dropdown="true"]')) == 1,\
        'just one .main_nav__classifieds w/ data-dropdown=true'

    assert len(html('nav.main_nav > div.main_nav__search'
        '[data-dropdown="true"]')) == 1,\
        'just one .main_nav__search w/ data-dropdown=true'

    assert len(html('nav.main_nav > div.main_nav__tags')) == 1,\
        'just one .main_nav__tags'

    assert len(html('nav.main_nav > div.main_nav__date')) == 1,\
        'just one .main_nav__date'


def test_nav_services_macro_should_have_expected_links(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_services()
    html = lxml.html.fromstring(html_str).cssselect
    assert html('li > a[href="http://www.zeitabo.de/?mcwt=2009_07_0002"]')[0]\
        is not None, 'No link for zeitabo.de'
    assert html('li > a[href="http://shop.zeit.de?et=l6VVNm&et_cid=42&'
        'et_lid=175&et_sub=Startseite_header"]'
        '[id="hp.global.topnav.links.shop"]')[0] is not None,\
        'No link for shop.zeit.de'
    assert html('li > a[href="https://premium.zeit.de/?wt_mc=pm.intern.fix.'
        'zeitde.fix.dach.text.epaper"]'
        '[id="hp.global.topnav.links.epaper"]')[0]\
        is not None, 'No link for premium.zeit.de'
    assert html('li > a[href="https://premium.zeit.de/abo/digitalpaket5'
        '?wt_mc=pm.intern.fix.zeitde.fix.dach.text.audio"][id="hp.global.'
        'topnav.links.audio"]')[0] is not None,\
        'No link for premium.zeit.de AUDIO'
    assert html('li > a[href="https://premium.zeit.de/abo/appsios?'
        'wt_mc=pm.intern.fix.zeitde.fix.dach.text.apps"][id="hp.global.topnav'
        '.links.apps"]')[0] is not None, 'No link for premium.zeit.de APPS'
    assert html('li > a[href="http://www.zeit.de/archiv"][id="hp.global.'\
        'topnav.links.archiv"]')[0] is not None, 'No link for Archiv'


def test_nav_classifieds_macro_should_have_expected_structure(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_classifieds()
    html = lxml.html.fromstring(html_str).cssselect
    assert html('li > a[href="http://jobs.zeit.de/"]'
        '[id="hp.global.topnav.links.jobs"]')[0]\
        is not None, 'No link for job.zeit.de'
    assert html('li > a[href="http://www.zeit.de/angebote/partnersuche/index?'
        'pscode=01_100_20003_0001_0001_0005_empty_AF00ID_GV00ID"]'
        '[id="hp.global.topnav.links.partnersuche"]')[0] is not None,\
        'Link for partnersuche not present'
    assert len(html('li.main_nav__classifieds__more')) == 1, 'No classifieds'
    assert html('li > a[href="http://zeit.immowelt.de/"]'
        '[id="hp.global.topnav.links.immobilien"][rel="nofollow"]')[0]\
        is not None, 'No link for zeit.immowelt.de'
    assert html('li > a[href="http://automarkt.zeit.de/"]'
        '[id="hp.global.topnav.links.automarkt"]')[0]\
        is not None, 'No link for Automarkt'


def test_nav_community_macro_should_render_a_login(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_community()
    html = lxml.html.fromstring(html_str).cssselect
    print html_str
    assert html('a[href="http://community.zeit.de/user/login?destination='
        'http://www.zeit.de/index"]'
        '[rel="nofollow"]'
        '[class="user"]'
        '[id="drupal_login"]')[0] is not None, 'Community login is missing'


def test_nav_main_nav_logo_should_create_a_logo_link(jinja2_env):
    tpl = jinja2_env.get_template(
        'zeit.web.site:templates/inc/nav_main.html')
    html_str = tpl.module.main_nav_logo()
    html = lxml.html.fromstring(html_str).cssselect
    assert html('a[href="http://www.zeit.de/index"]'
        '[title="Nachrichten auf ZEIT ONLINE"]'
        '[class="icon-zon-logo-desktop"]'
        '[id="hp.global.topnav.centerpages.logo"]')[0] is not None,\
        'Logo link is missing'


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
    assert '<nav class="main_nav">' in output
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
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html(
        'a[href="http://community.zeit.de/user/login?"]') is not None, (
        'Link to login form is invalid')
    assert html('span.main_nav__community__image') is not None, (
        'span.main_nav__community__image is invalid')
    assert 'Anmelden' in lxml.etree.tostring(
        html('a[id="drupal_login"]')[0]), (
        'Link to login has invalid label')


def test_article_has_valid_logo_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html('a.icon-zon-logo-desktop'
                '[href="http://www.zeit.de/index"]'
                '[title="Nachrichten auf ZEIT ONLINE"]'
                '[id="hp.global.topnav.centerpages.logo"]') is not None, (
        'Element a.icon-zon-logo-desktop is invalid')


def test_article_has_valid_burger_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html('div.logo_bar__menue__image'
                '.main_nav__icon--plain'
                '.icon-zon-logo-navigation_menu') is not None, (
        'Element div.main_nav__icon--plain is invalid')
    assert html('div.logo_bar__menue__image'
                '.main_nav__icon--hover'
                '.icon-zon-logo-navigation_menu-hover') is not None, (
        'Element .main_nav__icon--hover is invalid')


def test_article_has_valid_search_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html('form.search'
                '[accept-charset="utf-8"]'
                '[method="get"]'
                '[role="search"]'
                '[action="http://www.zeit.de/suche/index"]') is not None, (
        'Element form.search is invalid')
    assert html('label.hideme[for="q"]') is not None, (
        'label.hideme is invalid')
    assert html('label.hideme[for="q"]')[0].text == 'suchen', (
        'Element label.hideme has wrong text')
    assert html('button.search__button'
                '[type="submit"]'
                '[tabindex="2"]') is not None, (
        'Element button.search__button is invalid')
    assert html('span.icon-zon-logo-navigation_suche.search__button__image'
                '.main_nav__icon--plain') is not None, (
        'Element span in invalid')
    assert html('span.icon-zon-logo-navigation_suche-hover'
                '.search__button__image'
                '.main_nav__icon--hover')[0].text is None, (
        'Element span is not empty')
    assert html('input.search__input'
                '[id="q"]'
                '[name="q"]'
                '[type="search"]'
                '[placeholder="Suche"]'
                '[tabindex="1"]') is not None, (
        'Element input.search__input is invalid')
    assert html('button.search__close'
                '[type="submit"]'
                '[tabindex="2"]') is not None, (
        'Element button.search__close is invalid')
    assert html('span.icon-zon-logo-navigation_close-small'
                '.search__close__image')[0].text is None, (
        'Element span.icon-zon-logo-navigation_close-small is not empty')


def test_article_has_valid_tag_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert 'Schwerpunkte' in html('span.main_nav__tags__label')[0].text, (
        'Element main_nav__tags__label is invalid')
    assert html('ul'), 'Missing ul'


def test_article_has_valid_nav_date_structure(testserver, testbrowser):
    browser = testbrowser('%s/centerpage/zeitonline' % testserver.url)
    date = '3. September 2014 10:50 Uhr'
    html_str = browser.contents
    html = lxml.html.fromstring(html_str).cssselect
    assert html('div.main_nav__date')[0].text == date, (
        'Date is invalid')
