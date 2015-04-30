{% set area = area | automatize %}

{% extends "zeit.web.site:templates/inc/area/default.html" %}

{% block before_module_list %}
<div class="search-counter">
    {{ area.hits | default(0) | pluralize('Keine Ergebnisse', '{} Ergebnis', '{} Ergebnisse') }}
<div>
{% endblock %}

{% block after_module_list %}
<div class="search-pager">
    {% if area.pagination | length %}
        <div>Nächste Seite</div>
    {% endif %}
    <ul>
    {% for num, href in area.pagination %}
        <li>
            {% if href %}<a href="{{ href }}">{% endif %}
                {{ num if num else '...' }}
            {% if href %}</a>{% endif %}
        </li>
    {% endfor %}
    </ul>
</div>
{% endblock %}
