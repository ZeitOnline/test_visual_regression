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
        <a class="search-counter__link{% if area.sort_order == 'relevanz' %} search-counter__link--marked{% endif %}" href="{{ view.request | append_get_params(sort='relevanz') }}">Relevanz</a>
        <a class="search-counter__link{% if area.sort_order == 'aktuell' %} search-counter__link--marked{% endif %}" href={{ view.request | append_get_params(sort='aktuell') }}>Aktualität</a>
    </nav>
</div>
{% endblock %}

{% block after_module_list %}
{% if area.pagination %}
<div class="pager">
    {% if area.current_page == area.total_pages %}
    <a class="pager__button pager__button--previous" href="{{ view.request | append_get_params(p=area.current_page-1) }}">Vorherige Seite</a>
    {% else %}
    <a class="pager__button pager__button--next" href="{{ view.request | append_get_params(p=area.current_page+1) }}">Nächste Seite</a>
    {% endif %}
    <ul class="pager__pages">
        {% for num in area.pagination %}
        <li class="pager__page{% if num == area.current_page %} pager__page--current{% endif %}">
            {%- if num == area.current_page -%}
                <span>{{ num }}</span>
            {%- elif num -%}
                <a href="{{ view.request | append_get_params(p=num) }}">{{ num }}</a>
            {%- else -%}
                <span>…</span>
            {%- endif -%}
        </li>
        {% endfor %}
    </ul>
</div>
{% endif %}
{% endblock %}
