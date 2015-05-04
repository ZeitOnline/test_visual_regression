{% set area = area | get_results %}

{% extends "zeit.web.site:templates/inc/area/default.html" %}

{% block before_module_list %}
<div class="search-counter">
    <div class="search-counter__hits">
        {{ area.hits | default(0) | pluralize('Keine Suchergebnisse', '{} Suchergebnis', '{} Suchergebnisse') }}
        {% if area.query %}für &raquo;{{ area.query }}&laquo;{% endif %}
    </div>
    <nav>
        <span class="search-counter__label">Sortieren nach</span>
        <a class="search-counter__link{% if area.sort_order == 'relevanz' %} search-counter__link--marked{% endif %}" href={{ view.path_with_params(sort='relevanz') }}>Relevanz</a>
        <a class="search-counter__link{% if area.sort_order == 'aktuell' %} search-counter__link--marked{% endif %}" href={{ view.path_with_params(sort='aktuell') }}>Aktualität</a>
    </nav>
</div>
{% endblock %}

{% block after_module_list %}
<div class="search-pager" id="search-nav">
    {# if area.next_page #}
    <a class="search-pager__next" href="#{{ area.next_page }}">Nächste Seite</a>
    {# endif #}
    <ul class="search-pager__pages">
        {% for num in area.pagination %}
        <li class="search-pager__page {% if num == area.current_page %} search-pager__page--current {% endif %}">
            {% if num == area.current_page %}
                {{ num }}
            {% elif num %}
                <a class="search-pager__link" href="#{{ num }}">{{ num }}</a>
            {% else %}
                <span>…</span>
            {% endif %}
        </li>
        {% endfor %}
    </ul>
</div>
{% endblock %}
