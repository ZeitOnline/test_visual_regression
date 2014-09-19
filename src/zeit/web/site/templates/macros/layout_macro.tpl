<!-- new nav -->
{% macro main_nav(is_full_width,request) -%}
    <nav class="main_nav">

        <!-- logo -->
        <div class="logo_bar">
            <div class="logo_bar__image">{{ main_nav_logo() }}</div>
            <div class="logo_bar__menue">{{ main_nav_burger() }}</div>
        </div>

        <!-- special teaser -->
        <div class="main_nav__teaser">{{ main_nav_teaser() }}</div>

        <!-- wrap start -->
        <div class="main_nav__community" data-dropdown="true">{{ main_nav_community() }}</div>
        <div class="main_nav__ressorts" data-dropdown="true">
                {{ main_nav_ressorts() }}
        </div>
        <div class="main_nav__services" data-dropdown="true">{{ main_nav_services() }}</div>
        <div class="main_nav__classifieds" data-dropdown="true">{{ main_nav_classifieds() }}</div>
        <div class="main_nav__search" data-dropdown="true">{{ main_nav_search() }}</div>
        <!-- wrap end -->

        <!-- please don't break line here, due to inline-block state -->
        <div class="main_nav__tags">{{ main_nav_tags() }}</div><div class="main_nav__date">{{ main_nav_date() }}</div>

    </nav>
{%- endmacro %}

{% macro main_nav_services() -%}
    <ul>
        <li>
            <a href="http://www.zeitabo.de/?mcwt=2009_07_0002" id="hp.global.topnav.links.abo">
                Abo
            </a>
        </li>
        <li>
            <a href="http://shop.zeit.de?et=l6VVNm&amp;et_cid=42&amp;et_lid=175&amp;et_sub=Startseite_header" id="hp.global.topnav.links.shop">
                Shop
            </a>
        </li>
        <li>
            <a href="https://premium.zeit.de/?wt_mc=pm.intern.fix.zeitde.fix.dach.text.epaper" id="hp.global.topnav.links.epaper">
                E-Paper
            </a>
        </li>
        <li>
            <a href="https://premium.zeit.de/abo/digitalpaket5?wt_mc=pm.intern.fix.zeitde.fix.dach.text.audio" id="hp.global.topnav.links.audio">
                Audio
            </a>
        </li>
        <li>
            <a href="https://premium.zeit.de/abo/appsios?wt_mc=pm.intern.fix.zeitde.fix.dach.text.apps" id="hp.global.topnav.links.apps">
                Apps
            </a>
        </li>
        <li>
            <a href="http://www.zeit.de/archiv" id="hp.global.topnav.links.archiv">
                Archiv
            </a>
        </li>
    </ul>
{%- endmacro %}

{% macro main_nav_classifieds() -%}
    <ul>
        <li>
            <a href="http://jobs.zeit.de/" id="hp.global.topnav.links.jobs">
                Jobs
            </a>
        </li>
        <li>
            <a href="http://www.zeit.de/angebote/partnersuche/index?pscode=01_100_20003_0001_0001_0005_empty_AF00ID_GV00ID" id="hp.global.topnav.links.partnersuche">
                Partnersuche
            </a>
        </li>
        <li class="main_nav__classifieds__more">
            <a href="#">
                mehr
                <span class="main_nav__classifieds__more__image main_nav__icon--plain icon-zon-logo-navigation_dropdown"></span><span class="main_nav__classifieds__more__image main_nav__icon--hover icon-zon-logo-navigation_dropdown-hover"></span>
            </a>
        </li>
        <li>
            <a href="http://zeit.immowelt.de/" rel="nofollow" id="hp.global.topnav.links.immobilien">
                Immobilien
            </a>
        </li>
        <li>
            <a href="http://automarkt.zeit.de/" id="hp.global.topnav.links.automarkt">
                Automarkt
            </a>
        </li>
    </ul>
{%- endmacro %}

{% macro main_nav_community() -%}
    <a href="http://community.zeit.de/user/login?destination=http://www.zeit.de/index" rel="nofollow" class="user" id="drupal_login">
        <span class="main_nav__community__image icon-zon-logo-navigation_login"></span>
        Anmelden
    </a>
{%- endmacro %}

{% macro main_nav_logo() -%}
    <a href="http://www.zeit.de/index" title="Nachrichten auf ZEIT ONLINE" class="icon-zon-logo-desktop" id="hp.global.topnav.centerpages.logo">
        <!--start: title-->Nachrichten auf ZEIT ONLINE<!--end: title-->
    </a>
{%- endmacro %}

{% macro main_nav_burger() -%}
    <a href="#">
        <div class="logo_bar__menue__image main_nav__icon--plain icon-zon-logo-navigation_menu"></div>
        <div class="logo_bar__menue__image main_nav__icon--hover icon-zon-logo-navigation_menu-hover"></div>
    </a>
{%- endmacro %}

{% macro main_nav_teaser() -%}
    <!-- planned special teaser -->
{%- endmacro %}

{% macro main_nav_search() -%}
    <form accept-charset="utf-8" method="get" class="search" role="search" action="http://www.zeit.de/suche/index">
        <label for="q" class="hideme">suchen</label>
        <button class="search__button" type="submit" tabindex="2">
            <a href="#">
                <span class="icon-zon-logo-navigation_suche search__button__image main_nav__icon--plain"></span>
                <span class="icon-zon-logo-navigation_suche-hover search__button__image main_nav__icon--hover"></span>
            </a>
        </button>
        <input class="search__input" id="q" name="q" type="search" placeholder="Suche" tabindex="1">
        <button class="search__close" type="submit" tabindex="2">
            <span class="icon-zon-logo-navigation_close-small search__close__image"></span>
        </button>
    </form>
{%- endmacro %}

{% macro main_nav_ressorts() -%}
    <nav role="navigation">
        <ul class="primary-nav">
            <li class="primary-nav__item">
                <a class="primary-nav__link" href="#">Politik</a>
            </li>
            <li class="primary-nav__item">
                <a class="primary-nav__link primary-nav__link--current" href="#">Gesellschaft</a>
            </li>
            <li class="primary-nav__item">
                <a class="primary-nav__link" href="#">Wirtschaft</a>
            </li>
            <li class="primary-nav__item">
                <a class="primary-nav__link" href="#">Kultur</a>
            </li>
            <li class="primary-nav__item">
                <a class="primary-nav__link" href="#">Wissen</a>
            </li>
            <li class="primary-nav__item">
                <a class="primary-nav__link" href="#">Digital</a>
            </li>
            <li class="primary-nav__item">
                <a class="primary-nav__link" href="#">Studium</a>
            </li>
            <li class="primary-nav__item">
                <a class="primary-nav__link" href="#">Karriere</a>
            </li>
            <li class="primary-nav__item">
                <a class="primary-nav__link" href="#">Reise</a>
            </li>
            <li class="primary-nav__item">
                <a class="primary-nav__link" href="#">Sport</a>
            </li>
            <li class="primary-nav__item">
                <a class="primary-nav__link" href="#">Spiele</a>
            </li>
        </ul>
    </nav>
{%- endmacro %}

{% macro main_nav_tags() -%}
    <!-- be careful with line break: display-block alignment -->
    <span class="main_nav__tags__label">
        Schwerpunkte
    </span><ul>
        <li>Ukraine Krise</li>
        <li>Kämpfe im Irak</li>
        <li>Wahl in Sachsen</li>
    </ul>
{%- endmacro %}

{% macro main_nav_date(date='3. September 2014 10:50 Uhr') -%}
    {{ date }}
{%- endmacro %}
