{% macro date_meta(view) -%}
    {% if view.date_last_published_semantic %}
        <meta name="last-modified" content="{{ view.date_last_published_semantic }}"/>
        <meta http-equiv="last-modified" content="{{ view.date_last_published_semantic }}"/>
    {% else %}
        <meta name="last-modified" content="{{ view.date_first_released_meta }}"/>
        <meta http-equiv="last-modified" content="{{ view.date_first_released_meta }}"/>
    {% endif %}
    <meta name="date" content="{{ view.date_first_released_meta }}"/>
{%- endmacro %}

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

{% macro sharing_meta(obj, request) -%}
    <meta name="twitter:card" content="{{obj.twitter_card_type}}">
    <meta name="twitter:site" content="@zeitonline">
    <meta name="twitter:creator" content="@zeitonline">
    <meta name="twitter:title" content="{{obj.title}}">
    <meta name="twitter:description" content="{{obj.subtitle}}">
    <meta property="og:site_name" content="ZEIT ONLINE">
    <meta property="fb:admins" content="595098294">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{{obj.title or 'ZEITmagazin ONLINE'}}">
    <meta property="og:description" content="{{obj.subtitle or 'Mode&Design, Essen&Trinken, Leben'}}">
    <meta property="og:url" content="{{obj.article_url or 'http://' + request.host + request.path_info}}">
    {% if obj.image_group -%}
        <meta property="og:image" content="{{ obj.image_group|sharing_image_url(image_pattern='og-image') }}">
        <link itemprop="image" rel="image_src" href="{{ obj.image_group|sharing_image_url(image_pattern='og-image') }}">
        {% if obj.twitter_card_type == 'summary' -%}
            <meta name="twitter:image:src" content="{{ obj.image_group|sharing_image_url(image_pattern='twitter-image-small') }}">
        {% else -%}
            <meta name="twitter:image:src" content="{{ obj.image_group|sharing_image_url(image_pattern='twitter-image-large') }}">
        {% endif -%}
    {% endif -%}
{%- endmacro %}

{% macro main_nav(is_full_width,request) -%}
    <nav class="main-nav has-hover {% if is_full_width %}is-full-width{% endif %}" id="js-main-nav" itemscope itemtype="http://schema.org/SiteNavigationElement">
        <div class="main-nav__wrap">
            <a href="http://www.zeit.de/zeit-magazin/index" class="main-nav__logo" itemscope itemtype="http://schema.org/Organization" id="hp.zm.topnav.logo./zeit-magazin/index">
                <meta itemprop="name" content="Zeit Online">
                <h1 class="main-nav__logo__wrap">
                    <span class="main-nav__logo__img icon-logo-zmo-large" itemprop="logo" title="ZEITmagazin">ZEITmagazin ONLINE</span>
                    <span class="main-nav__logo__img icon-logo-zmo-small"></span>
                </h1>
            </a>
            <div class="main-nav__menu">
                <header class="main-nav__menu__head" id="js-main-nav-trigger">
                    <div class="main-nav__menu__head__headline"></div>
                    <div class="main-nav__menu__head__hamburger">Menu Öffnen</div>
                </header>
                <div class="main-nav__menu__content" id="js-main-nav-content">
                    <div class="main-nav__section main-nav__ressorts">
                        <div class="main-nav__ressorts__slider" id="js-main-nav-ressorts-slider-container">
                            <div class="main-nav__ressorts__slider-arrow--left icon-arrow-left is-inactive"></div>
                            <div class="main-nav__ressorts__slider-arrow--right icon-arrow-right"></div>
                            <div class="main-nav__ressorts__slider-strip" id="js-main-nav-ressorts-slider-strip">
                                <a href="http://{{request.host}}/zeit-magazin/mode-design/index" id="hp.zm.topnav.centerpages.mode./zeit-magazin/mode-design/index">Mode &amp; Design</a>
                                <a href="http://{{request.host}}/zeit-magazin/essen-trinken/index" id="hp.zm.topnav.centerpages.essen./zeit-magazin/essen-trinken/index">Essen &amp; Trinken</a>
                                <a href="http://{{request.host}}/zeit-magazin/leben/index" id="hp.zm.topnav.centerpages.leben./zeit-magazin/leben/index">Leben</a>
                            </div>
                        </div>
                    </div>
                    <div class="main-nav__section main-nav__only-small">
                        <a href="http://www.zeit.de/index" id="hp.zm.topnav.links.zon./index">» ZEIT ONLINE</a>
                    </div>
                    <div class="main-nav__section main-nav__service-primary">
                        <a href="http://www.zeitabo.de/?mcwt=2009_07_0002" id="hp.zm.topnav.links.abo.//www.zeitabo.de">Abo</a>
                        <a href="http://shop.zeit.de/?et=l6VVNm&amp;et_cid=42&amp;et_lid=175&amp;et_sub=Startseite_header" id="hp.zm.topnav.links.shop.//shop.zeit.de">Shop</a>
                        <a href="https://premium.zeit.de/?wt_mc=pm.intern.fix.zmo.fix.dach.text.epaper" id="hp.zm.topnav.links.epaper.//premium.zeit.de">ePaper</a>
                    </div>
                    <div class="main-nav__aside">
                        <div class="main-nav__section main-nav__only-full">
                            <a href="http://www.zeit.de/index" id="hp.zm.topnav.links.zon./index">» ZEIT ONLINE</a>
                        </div>
                        <div class="main-nav__section main-nav__service">
                            <span class="main-nav__section__trigger icon-arrow-down js-main-nav-section-trigger"><span class="main-nav__section__text">Service</span></span>
                            <div class="main-nav__section__content js-main-nav-section-content">
                                <a href="http://www.zeit.de/campus/index" id="hp.zm.topnav.links.zeitcampus./campus/index">ZEITCampus</a>
                                <a href="http://www.zeit.de/wissen/zeit-geschichte/index" id="hp.zm.topnav.links.zeitgeschichte./wissen/zeit-geschichte/index">ZEITGeschichte</a>
                                <a href="http://www.zeit.de/wissen/zeit-wissen/index" id="hp.zm.topnav.links.zeitwissen./wissen/zeit-wissen/index">ZEITWissen</a>
                                <a href="http://www.zeit.de/angebote/partnersuche/index?pscode=01_100_20003_0001_0001_0005_empty_AF00ID_GV00ID" id="hp.zm.topnav.links.partnersuche./angebote/partnersuche/index">Partnersuche</a>
                                <a href="http://zeit.immowelt.de/" id="hp.zm.topnav.links.immobilien.//zeit.immowelt.de">Immobilien</a>
                                <a href="http://automarkt.zeit.de/" id="hp.zm.topnav.links.automarkt.//automarkt.zeit.de">Automarkt</a>
                                <a href="http://jobs.zeit.de/" id="hp.zm.topnav.links.jobs.//jobs.zeit.de">Jobs</a>
                                <a href="https://premium.zeit.de/abo/appsios?wt_mc=pm.intern.fix.zmo.fix.dach.text.apps" id="hp.zm.topnav.links.apps.//premium.zeit.de/abo/appsios">Apps</a>
                                <a href="https://premium.zeit.de/abo/digitalpaket5?wt_mc=pm.intern.fix.zmo.fix.dach.text.audio" id="hp.zm.topnav.links.audio.//premium.zeit.de/abo/digitalpaket5">Audio</a>
                                <a href="http://www.zeit.de/archiv" id="hp.zm.topnav.links.archiv./archiv">Archiv</a>
                                <a href="http://www.zeit.de/spiele/index" id="hp.zm.topnav.links.spiele./spiele/index">Spiele</a>
                            </div>
                        </div>
<!--
                        <div class="main-nav__section main-nav__search">
                            <span class="main-nav__section__trigger icon-search js-main-nav-section-trigger"><span class="main-nav__section__text">Suche</span></span>
                            <div class="main-nav__section__content js-main-nav-section-content">
                                <form action="http://www.zeit.de/suche/index" role="search" method="get" class="main-nav__search__form">
                                    <input class="main-nav__search__input" type="text" name="q" size="20" placeholder="Suchbegriff …">
                                    <input class="main-nav__search__submit" type="submit" value="Suchen">
                                </form>
                            </div>
                        </div>
-->
                        <div class="main-nav__section main-nav__community">
                            {% if request.app_info.authenticated %}
                                {{ head_user_is_logged_in_true(request) }}
                            {%- else -%}
                                {{ head_user_is_logged_in_false(request) }}
                            {%- endif -%}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </nav>
{%- endmacro %}

{% macro head_user_is_logged_in_true(request)  %}
    <span class="main-nav__section__trigger js-main-nav-section-trigger">
        {% if request.app_info.user.picture %}
            <span class="main-nav__community__icon" style="background-image: url({{ request.app_info.community_host }}{{ request.app_info.user.picture }})"></span>
        {%- else -%}
            <span class="main-nav__community__icon icon-avatar-std"></span>
        {%- endif -%}
    </span>
    <div class="main-nav__section__content js-main-nav-section-content">
        <a href="{{ request.app_info.community_host }}user/{{ request.app_info.user.uid }}" id="hp.zm.topnav.community.account">Account</a>
        <a href="{{ request.app_info.community_host }}{{ request.app_info.community_paths.logout }}?destination={{ request.url }}" id="hp.zm.topnav.community.logout">Logout</a>
    </div>
{%- endmacro %}

{% macro head_user_is_logged_in_false(request)  %}
    <a href="{{ request.app_info.community_host }}{{ request.app_info.community_paths.login }}?destination={{ request.url }}" id="hp.zm.topnav.community.login">Anmelden</a>
{%- endmacro %}

{% macro copyrights(cr_list) -%}
    <div class="copyrights">
        <a class="js-toggle-copyrights copyrights__close copyrights__close--cross icon-copyrights-close"></a>
        <section class="copyrights__wrapper is-centered is-constrained">
            <span class="copyrights__title">Bildrechte auf dieser Seite</span>
            <ul class="copyrights__list">
                {%- for cr in cr_list -%}
                <li class="copyrights__entry">
                    <div class="copyrights__entry__image" style="background-image: url({{ cr.image }});"></div>
                    <span class="copyrights__entry__label">
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

{% macro adplace( banner, view ) -%}
    {% set kw = 'iqadtile' ~ banner.tile ~ ',' ~ view.adwords|join(',') -%}
    {% set pagetype = 'centerpage' if 'centerpage' in view.banner_channel else 'article' -%}
    {% if view.context.advertising_enabled -%}
    <!-- Bannerplatz: "{{banner.name}}", Tile: {{banner.tile}} -->
    <div id="iqadtile{{ banner.tile }}" class="ad__{{ banner.name }} ad__on__{{ pagetype }} ad__width_{{ banner.noscript_width_height[0] }} ad__min__{{ banner.min_width }}">
        {% if banner.label -%}
        <div class="ad__{{ banner.name }}__label">{{ banner.label }}</div>
        {% endif -%}
        <div class="ad__{{ banner.name }}__inner">
            <script type="text/javascript">
                if ( window.ZMO.clientWidth >= {{ banner.min_width|default(0) }} ) {
                    document.write('<script src="http://ad.de.doubleclick.net/adj/zeitonline/{{ view.banner_channel }}{% if banner.dcopt %};dcopt={{ banner.dcopt }}{% endif %};tile={{ banner.tile }};' + n_pbt + ';sz={{ banner.sizes|join(',') }};kw={{ kw }},' + iqd_TestKW {% if banner.diuqilon %}+ window.diuqilon {% endif %}+ ';ord=' + IQD_varPack.ord + '?" type="text/javascript"><\/script>');
                }
            </script>
            <noscript>
            <div>
                <a href="http://ad.de.doubleclick.net/jump/zeitonline/{{ view.banner_channel }};tile={{ banner.tile }};sz={{ banner.sizes|join(',') }};kw={{ kw }};ord=123456789?" rel="nofollow">
                    <img src="http://ad.de.doubleclick.net/ad/zeitonline/{{ view.banner_channel }};tile={{ banner.tile }};sz={{ banner.sizes|join(',') }};kw={{ kw }};ord=123456789?" width="{{ banner.noscript_width_height[0] }}" height="{{ banner.noscript_width_height[1] }}" alt="">
            </a></div>
            </noscript>
        </div>
    </div>
    {%- endif %}
{%- endmacro %}

{% macro adplace_middle_mobile(item) -%}
    {% if item.tile == 7 -%}
    <!-- only integrate onces as equivalent to desktop tile 7 -->
        <div class="iqd_mobile__adplace--middle">
            <div id="sas_13557"></div>
        </div>
    {%- endif %}
{%- endmacro %}

{% macro insert_responsive_image(image, image_class, page_type) %}

    {% set alt = ''%}
    {% set title = ''%}

    {% if image.alt %}
        {% set alt = image.alt %}
        {% set title = image.title %}
    {% elif image.attr_alt %}
        {% set alt = image.attr_alt %}
        {% set title = image.attr_title %}
    {% endif %}

    {% if image %}
        <!--[if gt IE 8]><!-->
            <noscript data-src="{{image | default_image_url}}">
        <!--<![endif]-->
        {% if page_type == 'article' and image.href %}
            <a href="{{image.href}}">
        {% endif %}
                <img alt="{{alt}}" {% if title %}title="{{title}}" {% endif %}class="{{image_class | default('', true)}} figure__media" src="{{image | default_image_url}}" data-ratio="{{image.ratio}}">
        {% if page_type == 'article' and image.href %}
            </a>
        {% endif %}
        <!--[if gt IE 8]><!-->
            </noscript>
        <!--<![endif]-->
    {% endif %}
{% endmacro %}
