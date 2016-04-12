{% extends 'zeit.web.core:templates/macros/layout_macro.tpl' %}

{% macro breadcrumbs(crumbs) -%}
    <div class="breadcrumbs">
        <div class="breadcrumbs__list is-constrained is-centered">
            {% for crumb in crumbs -%}
                <div class="breadcrumbs__list__item" itemscope="itemscope" itemtype="http://data-vocabulary.org/Breadcrumb">
                {% if crumb[1] != '' -%}
                    <a href="{{crumb[1]}}" itemprop="url"><span itemprop="title">{{crumb[0]}}</span></a>
                {% else -%}
                    <span itemprop="title">{{crumb[0]}}</span>
                {% endif -%}
                </div>
                {% if not loop.last -%}
                &rsaquo;
                {% endif -%}
            {% endfor -%}
        </div>
    </div>
{%- endmacro %}

{% macro insert_responsive_image(image, image_class, page_type) %}
    {# TRASHME: I want to be replace by the new snazzy image.tpl #}
    {% if image %}
        {% set source = image | default_image_url %}
        <!--[if gt IE 8]><!-->
            <noscript data-src="{{ source }}">
        <!--<![endif]-->
        {% if page_type == 'article' and image.href %}
            <a href="{{ image.href }}">
        {% endif %}
                <img alt="{{ image.alt }}"{% if image.title %} title="{{ image.title }}"{% endif %} class="{{ image_class | default('', true) }} figure__media" src="{{ source }}" data-src="{{ source }}" data-ratio="{{ image.ratio }}"{% if image.itemprop %} itemprop="{{ image.itemprop }}"{% endif %}>
        {% if page_type == 'article' and image.href %}
            </a>
        {% endif %}
        <!--[if gt IE 8]><!-->
            </noscript>
        <!--<![endif]-->
    {% endif %}
{% endmacro %}

{% macro main_nav(is_full_width, request, is_advertorial=False, is_main_h1=True) -%}
    {% set title_tag = 'h1' if is_main_h1 else 'div' %}
    <nav class="main-nav has-hover {% if is_full_width %}is-full-width{% endif %}" id="js-main-nav" itemscope itemtype="http://schema.org/SiteNavigationElement">
        <div class="main-nav__wrap">
            <a href="{{ request.route_url('home') }}zeit-magazin/index" class="main-nav__logo" itemscope itemtype="http://schema.org/Organization" id="hp.zm.topnav.logo./zeit-magazin/index">
                <meta itemprop="name" content="Zeit Online">
                <{{ title_tag }} class="main-nav__logo__wrap">
                    {{ use_svg_icon('logo-zmo-large', 'main-nav__brand-logo main-nav__brand-logo--large main-nav__brand-logo--zmo-large', view.package) }}
                    {{ use_svg_icon('logo-zmo-small', 'main-nav__brand-logo main-nav__brand-logo--small main-nav__brand-logo--zmo-small', view.package) }}
                </{{ title_tag }}>
            </a>
            <div class="main-nav__menu">
                {% if is_advertorial %}
                    <div class="advertorial-navigation-title">Anzeige</div>
                {% endif %}

                <header class="main-nav__menu__head" id="js-main-nav-trigger">
                    <div class="main-nav__menu__head__hamburger">Menu Öffnen</div>
                </header>
                <div class="main-nav__menu__content" id="js-main-nav-content">
                    <div class="main-nav__section main-nav__ressorts">
                        <div class="main-nav__ressort-list">
                            <a href="{{ request.route_url('home') }}zeit-magazin/mode-design/index" id="hp.zm.topnav.centerpages.mode./zeit-magazin/mode-design/index">Mode &amp; Design</a>
                            <a href="{{ request.route_url('home') }}zeit-magazin/essen-trinken/index" id="hp.zm.topnav.centerpages.essen./zeit-magazin/essen-trinken/index">Essen &amp; Trinken</a>
                            <a href="{{ request.route_url('home') }}zeit-magazin/leben/index" id="hp.zm.topnav.centerpages.leben./zeit-magazin/leben/index">Leben</a>
                        </div>
                    </div>
                    <div class="main-nav__section main-nav__only-small">
                        <a href="{{ request.route_url('home') }}index" id="hp.zm.topnav.links.zon./index">» ZEIT ONLINE</a>
                    </div>
                    <div class="main-nav__section main-nav__service-primary">
                        <a href="http://www.zeitabo.de/?mcwt=2009_07_0002" id="hp.zm.topnav.links.abo.//www.zeitabo.de">Abo</a>
                        <a href="http://shop.zeit.de/?et=l6VVNm&amp;et_cid=42&amp;et_lid=175&amp;et_sub=Startseite_header" id="hp.zm.topnav.links.shop.//shop.zeit.de">Shop</a>
                        <a href="https://premium.zeit.de/?wt_mc=pm.intern.fix.zmo.fix.dach.text.epaper" id="hp.zm.topnav.links.epaper.//premium.zeit.de">ePaper</a>
                    </div>
                    <div class="main-nav__aside">
                        <div class="main-nav__section main-nav__only-full">
                            <a href="{{ request.route_url('home') }}index" id="hp.zm.topnav.links.zon./index">» ZEIT ONLINE</a>
                        </div>
                        <div class="main-nav__section main-nav__service">
                            <span class="main-nav__section__trigger js-main-nav-section-trigger"><span class="main-nav__section__text">Service</span>{{ use_svg_icon('arrow-down', 'main-nav__icon-arrow-down', view.package) }}</span>
                            <div class="main-nav__section__content js-main-nav-section-content">
                                <a href="{{ request.route_url('home') }}campus/index" id="hp.zm.topnav.links.zeitcampus./campus/index">ZEITCampus</a>
                                <a href="{{ request.route_url('home') }}wissen/zeit-geschichte/index" id="hp.zm.topnav.links.zeitgeschichte./wissen/zeit-geschichte/index">ZEITGeschichte</a>
                                <a href="{{ request.route_url('home') }}wissen/zeit-wissen/index" id="hp.zm.topnav.links.zeitwissen./wissen/zeit-wissen/index">ZEITWissen</a>
                                <a href="{{ request.route_url('home') }}angebote/partnersuche/index?pscode=01_100_20003_0001_0001_0005_empty_AF00ID_GV00ID" id="hp.zm.topnav.links.partnersuche./angebote/partnersuche/index">Partnersuche</a>
                                <a href="http://zeit.immowelt.de/" id="hp.zm.topnav.links.immobilien.//zeit.immowelt.de">Immobilien</a>
                                <a href="http://automarkt.zeit.de/" id="hp.zm.topnav.links.automarkt.//automarkt.zeit.de">Automarkt</a>
                                <a href="http://jobs.zeit.de/" id="hp.zm.topnav.links.jobs.//jobs.zeit.de">Jobs</a>
                                <a href="https://premium.zeit.de/abo/appsios?wt_mc=pm.intern.fix.zmo.fix.dach.text.apps" id="hp.zm.topnav.links.apps.//premium.zeit.de/abo/appsios">Apps</a>
                                <a href="https://premium.zeit.de/abo/digitalpaket5?wt_mc=pm.intern.fix.zmo.fix.dach.text.audio" id="hp.zm.topnav.links.audio.//premium.zeit.de/abo/digitalpaket5">Audio</a>
                                <a href="{{ request.route_url('home') }}archiv" id="hp.zm.topnav.links.archiv./archiv">Archiv</a>
                                <a href="{{ request.route_url('home') }}spiele/index" id="hp.zm.topnav.links.spiele./spiele/index">Spiele</a>
                            </div>
                        </div>
                        <div class="main-nav__section main-nav__community">
                            {% set esi_source = '{}login-state?for=magazin&context-uri={}'.format(request.route_url('home'), request.url) %}
                            {{ insert_esi(esi_source, 'Anmeldung nicht möglich') }}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </nav>
{%- endmacro %}

{% macro head_user_is_logged_in_true(request)  %}
    <span class="main-nav__section__trigger js-main-nav-section-trigger">
        {% if request.session.user.picture %}
            <span class="main-nav__avatar" style="background-image: url({{ request.session.user.picture }})"></span>
        {%- else -%}
            {{ use_svg_icon('avatar-std', 'main-nav__avatar', view.package) }}
        {%- endif -%}
    </span>
    <div class="main-nav__section__content js-main-nav-section-content">
        <a href="{{ request.registry.settings.community_host }}/user/{{ request.session.user.uid }}" id="hp.zm.topnav.community.account">Account</a>
        {% if request.registry.settings.sso_activate %}
            <a href="{{ request.registry.settings.sso_url }}/abmelden?url={{ request.url }}" id="hp.zm.topnav.community.logout">Logout</a>
        {% else %}
            <a href="{{ request.registry.settings.community_host }}/logout?destination={{ request.url }}" id="hp.zm.topnav.community.logout">Logout</a>
        {% endif %}
    </div>
{%- endmacro %}

{% macro head_user_is_logged_in_false(request) -%}
    {% if request.registry.settings.sso_activate %}
        <a href="{{ request.registry.settings.sso_url }}/anmelden?url={{ request.url }}" id="hp.zm.topnav.community.login">Anmelden</a>
    {% else %}
        <a href="{{ request.registry.settings.community_host }}/user/login?destination={{ request.url }}" id="hp.zm.topnav.community.login">Anmelden</a>
    {% endif %}
{%- endmacro %}

{% macro copyrights(cr_list) -%}
    <div id="copyrights" class="copyrights">
        {{ use_svg_icon('copyrights-close', 'js-toggle-copyrights copyrights__close copyrights__close--icon', view.package) }}
        <section class="copyrights__wrapper is-centered is-constrained">
            <span class="copyrights__title">Bildrechte auf dieser Seite</span>
            <ul class="copyrights__list">
                {%- for cr in cr_list -%}
                <li class="copyrights__entry">
                    <div class="copyrights__image" style="background-image: url({{ cr.image }});"></div>
                    <span class="copyrights__label">
                        {%- if cr.link -%}
                            <a href="{{ cr.link }}"{% if cr.nofollow %} rel="nofollow"{% endif %}>{{ cr.label }}</a>
                        {%- else -%}
                            {{ cr.label }}
                        {%- endif -%}
                    </span>
                </li>
                {%- endfor -%}
            </ul>
        </section>
        <a class="js-toggle-copyrights copyrights__close copyrights__close--label">Bereich schließen</a>
        <div style="clear:both"></div>
    </div>
{%- endmacro %}
