{% extends 'zeit.web.core:templates/macros/centerpage_macro.tpl' %}

{% macro section_heading(title, label='', path=None, view=None, tracking_slug=None, unpadded=None) -%}
    <div class="section-heading {% if unpadded %}section-heading--unpadded{% endif %}">
        <h3 class="section-heading__title">{{ title }}</h3>
        {% if path -%}
        <a href="{% if view %}{{ view.request.route_url('home') }}{% endif %}{{ path }}"
           class="section-heading__link {% if unpadded %}section-heading__link--unpadded{% endif %}"
            {%- if tracking_slug %} data-id="{{ tracking_slug }}"{% endif %}>
            <span class="section-heading__text">{{ label }}</span>
        </a>
        {%- endif %}
    </div>
{%- endmacro %}
