{% set area = area | automatize %}

{% extends "zeit.web.site:templates/inc/area/default.html" %}

{% block before_module_list %}
<div class="search-counter">
    <h2>
        {{ area.hits | default(0) | pluralize('Keine Suchergebnisse', '{} Suchergebnis', '{} Suchergebnisse') }}
        {% if area.query %}f&uuml;r &raquo;{{ area.query }}&laquo;{% endif %}
    </h2>
    <p>
        Sortieren nach
        <a style="text-decoration:underline;" href={{ view.path_with_params(sort='relevanz') }}>Relevanz</a>
        <a style="text-decoration:underline;" href={{ view.path_with_params(sort='aktuell') }}>Aktualit&auml;t</a>
    </p>
<div>
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
