{% set area = area | automatize %}

{% extends "zeit.web.site:templates/inc/area/default.html" %}

{% block before_module_list %}
<div class="search-counter">
    <div class="search-counter__hits">
        {{ area.hits | default(0) | pluralize('Keine Suchergebnisse', '{} Suchergebnis', '{} Suchergebnisse') }}
        {% if area.query %}f&uuml;r &raquo;{{ area.query }}&laquo;{% endif %}
    </div>
    <nav>
        <span class="search-counter__label">Sortieren nach</span>
        <a class="search-counter__link{% if area.sort_order == 'relevanz' %} search-counter__link--marked{% endif %}" href={{ view.path_with_params(sort='relevanz') }}>Relevanz</a>
        <a class="search-counter__link{% if area.sort_order == 'aktuell' %} search-counter__link--marked{% endif %}" href={{ view.path_with_params(sort='aktuell') }}>Aktualit&auml;t</a>
    </nav>
</div>
{% endblock %}

{% block after_module_list %}
<div class="search-pager">
    {% if area.next_page %}
        <div style="display:inline;">
            <a href="#{{ area.next_page }}">N&auml;chste Seite</a>
        </div>
    {% endif %}
    <ul style="list-style-type:none;display:inline;">
    {% for num in area.pagination %}
        <li style="display:inline-block;">
            {% if num %}
                <a style="{{ 'font-weight:bolder;' if num == area.current_page else '' }}" href="#{{ num }}">{{ num }}</a>
            {% else %}
                <span>...</span>
            {% endif %}
        </li>
    {% endfor %}
    </ul>
</div>
{% endblock %}
