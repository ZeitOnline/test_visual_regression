{% set area = area | automatize %}

{% extends "zeit.web.site:templates/inc/area/default.html" %}

{% block before_module_list %}
<div class="search-counter">
    <h2>
        {{ area.hits | default(0) | pluralize('Keine Suchergebnisse', '{} Suchergebnis', '{} Suchergebnisse') }}
        {% if area.query %}f&uuml;r &raquo;{{ area.query }}&laquo;{% endif %}
    </h2>
    <p>Sortieren nach <a href={{ '#' }}>Relevanz</a> <a href={{ '#' }}>Aktualit&auml;t</a></p>
<div>
{% endblock %}

{% block after_module_list %}
<div class="search-pager">
    {% if area.pagination | length %}
        <div>N&auml;chste Seite</div>
    {% endif %}
    <ul style="list-style-type:none;">
    {% for num, href, active in area.pagination %}
        <li style="display:inline-block;">
            {% if href %}<a href="{{ href }}">{% endif %}
                <span style="{{ 'font-weight:bolder;' if active else '' }}">
                    {{ num if num else '...' }}
                </span>
            {% if href %}</a>{% endif %}
        </li>
    {% endfor %}
    </ul>
</div>
{% endblock %}
