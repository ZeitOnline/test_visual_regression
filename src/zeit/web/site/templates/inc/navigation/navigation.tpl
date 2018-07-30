{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama %}

<div class="header__brand" data-ct-row="lead">
    {% with tag_name = 'h1' if view.is_hp else 'div' -%}
    <{{ tag_name }} class="header__publisher">
        <a href="{{ request.route_url('home') }}index" title="Nachrichten auf ZEIT ONLINE" data-ct-label="logo">
            {{ lama.use_svg_icon('logo-zon-black', 'header__logo', view.package) }}
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

    <div class="nav__login" data-ct-row="usermenu" {% if view.framebuilder_loginstatus_disabled %} data-featuretoggle="disable-loginstatus"{% endif %}>
        {% block login %}
            {% set esi_source = '/login-state?for=site&context-uri={}'.format(request.url | urlquote_plus) %}
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
{%- endif -%}

</div>
