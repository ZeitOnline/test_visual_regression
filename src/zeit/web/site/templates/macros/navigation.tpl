{% macro main_nav(navigation, nav_class=None) -%}
    {% set nav_class = nav_class or 'main-nav' %}
    <ul class="{{ nav_class }}{% if nav_class == 'primary-nav' %} primary-nav--js-no-overflow{% endif %}">
        {% for i in navigation -%}
        {% set section = navigation[i] %}
        <li class="{{ nav_class }}__item" data-id="{{ section.item_id }}"{% if section.has_children() %} data-feature="dropdown"{% endif %}>
            <a class="{{ nav_class }}__link" href="{{ section.href | translate_url }}">{{ section.text }}</a>
            {% if section.has_children() -%}
                {{ main_nav(section, 'dropdown') }}
            {%- endif %}
        </li>
        {%- endfor %}
        {% if nav_class == 'primary-nav' %}
        <li class="{{ nav_class }}__item" data-feature="dropdown" data-id="more-dropdown">
            <a class="{{ nav_class }}__link" href="#">mehr</a>
            <ul class="dropdown">
                {% for i in navigation -%}
                {% set section = navigation[i] %}
                <li class="dropdown__item" data-id="{{ section.item_id }}"{% if section.has_children() %} data-feature="dropdown"{% endif %}>
                    <a class="dropdown__link" href="{{ section.href | translate_url }}">{{ section.text }}</a>
                    {% if section.has_children() -%}
                        {{ main_nav(section, 'dropdown') }}
                    {%- endif %}
                </li>
                {%- endfor %}
            </ul>
        </li>
        {% endif %}
    </ul>
{%- endmacro %}

{% macro main_nav_ressorts(navigation, nav_class=None) -%}
    <nav role="navigation">
        {{ main_nav(navigation, 'primary-nav') }}
    </nav>
{%- endmacro %}

{% macro main_nav_services(navigation, nav_css=None) -%}
    {{ main_nav(navigation, 'primary-nav-services') }}
{%- endmacro %}

{% macro main_nav_classifieds(navigation) -%}
    {{ main_nav(navigation, 'primary-nav-classifieds') }}
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
        <input class="search__input" id="q" name="q" type="search" placeholder="Suche" tabindex="1">
        <button class="search__button" type="submit" tabindex="2">
            <a>
                <span class="icon-zon-logo-navigation_suche search__button__image main_nav__icon--plain"></span>
                <span class="icon-zon-logo-navigation_suche-hover search__button__image main_nav__icon--hover"></span>
            </a>
        </button>
    </form>
{%- endmacro %}

{% macro main_nav_date(date='3. September 2014 10:50 Uhr') -%}
    {{ date }}
{%- endmacro %}

{% macro main_nav_tags(title, links) -%}
    <!-- be careful with line break: display-block alignment -->
    <span class="main_nav__tags__label">{{ title }}</span><ul>
        {% for label, link in links %}
            <li>
                <a href='{{link}}' title='{{label}}'>{{label}}</a>
            </li>
        {% endfor %}
    </ul>
{%- endmacro %}
