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
            {%- elif num == 1 -%}
                <a href="{{ view.request.url | remove_get_params('p') }}">{{ num }}</a>
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
