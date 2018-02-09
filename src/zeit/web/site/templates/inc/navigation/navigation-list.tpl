{% set items = navigation %}
{% set class = nav_class %}

<ul class="{{ class }}-list"{% if nav_id %} id="{{ nav_id }}" aria-hidden="true" data-ct-column{% endif %}>
{% for item in items.values() %}
    {% set id = item.item_id | pop_from_dotted_name -%}

    {% set link_css_class = '' %}
    {% if id in (view.ressort, view.sub_ressort) %}
        {% set link_css_class = '{}-link--current'.format(class) %}
    {% endif %}
    {% if class == 'nav__ressorts' and id == 'arbeit' and toggles('arbeit_hightlight_ressortnav') %}
        {% set link_css_class = '{}-link--arbeit-highlighted'.format(class) %}
    {% endif %}

    <li {%- if item.label %} class="{{ class }}-item--has-label" data-label="{{ item.label }}"{% endif %}
        {%- if item | length %} class="{{ class }}-item--has-dropdown"{% endif %}>
        <a href="{{ item.href | create_url }}"
            {%- if link_css_class %} class="{{ link_css_class }}" {% endif -%}
            {%- if item | length %} role="button" aria-controls="{{ item.text | lower }}" data-follow-mobile="true"{% endif %}
            {%- if site_navigation_element %} itemprop="url"{% endif %}>
            {%- if site_navigation_element -%}
                <span itemprop="name">{{ item.text }}</span>
            {%- else -%}
                {{- item.text -}}
            {%- endif -%}
        </a>
    {% if item | length -%}
        {%- set navigation = item -%}
        {%- set nav_class = "nav__dropdown" -%}
        {%- set nav_id = item.text | lower -%}
        {% include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" %}
    {%- endif -%}
    </li>
{% endfor %}

{% if class == 'nav__ressorts' %}
    <li class="{{ class }}-item--more {{ class }}-item--has-dropdown">
        <a href="#more-ressorts" role="button" aria-controls="more-ressorts" data-follow-mobile="true">mehr</a>
        <ul class="nav__dropdown-list" id="more-ressorts" aria-hidden="true" data-ct-column>
        </ul>
    </li>
    {% if toggles('dtag_navigation') -%}
    <li class="{{ class }}-item--featured-dtag">
        <a itemprop="url" href="{{ request.route_url('home') }}thema/d18">
            <svg viewBox="0 0 350 210" height="28" width="45" xmlns="http://www.w3.org/2000/svg"><path fill="#FB0" d="M50.9 166h11.8l5-37h14.5l-5 37H89l5-37h9v-10h-7.7l3.8-29H110V79h-9.5l5-35H93.8l-5 35H74.3l5-35H67.5l-5 35H53v11h8.1l-3.8 29H47v10h8.9l-5 37zm22-76h14.5l-3.8 29H69.1l3.8-29zM172.1 157.1c5.6-5.5 8.9-14.7 8.9-26.2V73.3c0-10-3.2-16.6-8.5-22.2S159 43.9 149 43.9h-26v122h24.5c10.5.1 19-3.3 24.6-8.8zM141 60h7.7c5.2 0 8.6.4 10.6 3 2 2.7 2.8 5.5 2.8 10.3v59.3c0 5.3-.9 10.2-2.9 12.7-2.1 2.5-5.4 4.7-10.4 4.7H141V60zM213 166h18V44h-17.7L195 54.5v18.7l18-13z"/><path fill="#FB0" d="M0 0v210h350V0H0zm335 195H15V15h320v180z"/><path fill="#FB0" d="M251 76.1c0-3.3.1-6.1.3-8.5.2-2.3.6-4.4 1.1-6.1.5-1.7 1.2-3.2 2-4.6.8-1.4 1.8-2.8 2.9-4.3 2.3-3 5.1-5.3 8.6-6.9 3.4-1.7 7.1-2.5 11.1-2.5s7.7.8 11.1 2.5 6.3 4 8.6 6.9c1.1 1.5 2.1 2.9 2.9 4.3.8 1.4 1.5 2.9 2 4.6s.9 3.7 1.1 6.1c.2 2.3.3 5.2.3 8.5 0 3.6-.1 6.7-.2 9.2s-.5 4.7-1 6.7c-.6 1.9-1.5 3.7-2.7 5.2s-2.8 3.2-4.9 4.9c2.1 1.6 3.7 3.2 4.9 4.8 1.2 1.6 2.1 3.5 2.7 5.6.6 2.2.9 4.8 1 8 .1 3.1.2 7 .2 11.5 0 3.8-.1 6.9-.3 9.3-.2 2.5-.4 4.6-.8 6.4-.3 1.8-.8 3.4-1.5 4.6-.6 1.3-1.4 2.6-2.3 3.9-1.9 3-4.7 5.5-8.2 7.6s-7.9 3.2-13 3.2-9.5-1.1-13-3.2-6.3-4.6-8.2-7.6c-.9-1.4-1.7-2.7-2.3-3.9-.6-1.3-1.1-2.8-1.5-4.6-.3-1.8-.6-4-.8-6.4-.2-2.5-.3-5.6-.3-9.3 0-4.6.1-8.4.2-11.5.1-3.1.5-5.8 1-8 .6-2.2 1.5-4 2.7-5.6s2.8-3.2 4.9-4.8c-2.1-1.7-3.7-3.3-4.9-4.9-1.2-1.5-2.1-3.3-2.7-5.2-.6-1.9-.9-4.2-1-6.7v-9.2zm34.5-6.9c0-2.4-.9-4.4-2.6-6.1-1.7-1.7-3.7-2.5-6-2.5s-4.3.8-6 2.5c-1.7 1.7-2.6 3.7-2.6 6.1V87c0 2.4.9 4.4 2.6 6.1s3.7 2.5 6 2.5 4.3-.8 6-2.5 2.6-3.7 2.6-6.1V69.2zm0 47.9c0-2.4-.9-4.4-2.6-6.1s-3.7-2.5-6-2.5-4.3.8-6 2.5-2.6 3.7-2.6 6.1V141c0 2.4.9 4.4 2.6 6.1 1.7 1.7 3.7 2.5 6 2.5s4.3-.8 6-2.5 2.6-3.7 2.6-6.1v-23.9z"/></svg>
        </a>
    </li>
    {% endif %}
{% endif %}
</ul>
