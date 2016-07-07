{% set items = navigation %}
{% set class = nav_class %}
<ul class="{{ class }}-list"{% if nav_id %} id="{{ nav_id }}" aria-hidden="true" data-ct-column{% endif %}>
{% for item in items.values() %}
    {% set id = item.item_id | pop_from_dotted_name -%}
    <li {%- if item.label %} class="{{ class }}-item--has-label" data-label="{{ item.label }}"{% endif %}
        {%- if item | length %} class="{{ class }}-item--has-dropdown"{% endif %}>
        <a href="{{ item.href | create_url }}"
            {%- if id in (view.ressort, view.sub_ressort) %} class="{{ class }}-link--current"{% endif %}
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
    <li class="{{ class }}-item--featured">
        <a itemprop="url" href="{{ request.route_url('home') }}zeit-magazin/index">
            <span itemprop="name">ZEITmagazin</span>
        </a>
    </li>
{% endif %}
</ul>
