{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

<div class="header__brand" data-ct-row="lead">
    {% with tag_name = 'h1' if view.is_hp else 'div' -%}
    <{{ tag_name }} class="header__publisher" id="publisher" itemprop="publisher" itemscope itemtype="http://schema.org/Organization">
        <a itemprop="url" href="{{ request.route_url('home') }}index" title="Nachrichten auf ZEIT ONLINE" data-ct-label="logo">
            <meta itemprop="name" content="ZEIT ONLINE">
            <span itemprop="logo" itemscope itemtype="http://schema.org/ImageObject">
                {{ lama.use_svg_icon('logo-zon-black', 'header__logo', view.package) }}
                {# The "logo" dimensions must not exceed 600x60 -#}
                <meta itemprop="url" content="{{ request.asset_host }}/images/structured-data-publisher-logo-zon.png">
                <meta itemprop="width" content="565">
                <meta itemprop="height" content="60">
            </span>
        </a>
    </{{ tag_name }}>
    {% endwith -%}

    <!-- special teaser -->
    {% block special_teaser -%}
        {% if view.is_advertorial -%}
        <div class="header__ad-label">{{ view.cap_title | default('Anzeige') }}</div>
        {%- else -%}
        <div class="header__teaser">{# planned special teaser #}</div>
        {%- endif %}
    {%- endblock special_teaser %}

    <a class="header__menu-link" href="#navigation" role="button" aria-controls="navigation" aria-label="Menü" data-ct-label="menu">
        {{ lama.use_svg_icon('menu', 'header__menu-icon header__menu-icon--menu', view.package) }}
        {{ lama.use_svg_icon('close', 'header__menu-icon header__menu-icon--close', view.package) }}
    </a>
</div>

<div class="nav" id="navigation">
    <nav class="nav__classifieds" data-ct-row="classifieds">
        {%- set navigation = view.navigation_classifieds -%}
        {%- set nav_class = 'nav__classifieds' -%}
        {%- include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" -%}
    </nav>

    <nav class="nav__services" data-ct-row="services">
        {%- set navigation = view.navigation_services -%}
        {%- set nav_class = 'nav__services' -%}
        {%- include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" -%}
    </nav>

    <div class="nav__login" data-ct-row="usermenu">
        {% block login %}
            {% set esi_source = '{}login-state?for=site&context-uri={}'.format(request.route_url('home'), request.url) %}
            {{ lama.insert_esi(esi_source, 'Anmeldung nicht möglich') }}
        {% endblock login %}
    </div>

    <div class="nav__search" data-ct-row="search">
        {%- if view.nav_show_search -%}
            {%- include "zeit.web.site:templates/inc/navigation/navigation-search.tpl" -%}
        {%- endif -%}
    </div>

{% if view.nav_show_ressorts %}
    <nav class="nav__ressorts" itemscope itemtype="http://schema.org/SiteNavigationElement" data-ct-row="mainnav">
        {%- set navigation = view.navigation -%}
        {%- set nav_class = 'nav__ressorts' -%}
        {%- set site_navigation_element = True -%}
        {%- include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" -%}
    </nav>
{% endif %}

{%- if view.is_hp -%}
    {% block metadata %}
    <div class="nav__metadata">
        {%- require topics = view.is_hp and view.context | topic_links -%}
            <div class="nav__tags" data-ct-row="article-tag">
                <span class="nav__label">{{ topics.title }}</span>
                {% for label, link in topics %}
                    <a href="{{ link }}" class="nav__tag">{{ label }}</a>
                {% endfor %}
            </div>
        {%- endrequire -%}
        {% set date = view.date_last_modified | format_timedelta(hours=3) %}
        {% if date %}
            <div class="nav__date">
                <time datetime="{{ view.date_last_modified | format_date('iso8601') }}">Aktualisiert {{ date }}</time>
            </div>
        {% endif %}
    </div>
    {% endblock metadata %}
{%- endif -%}

</div>
