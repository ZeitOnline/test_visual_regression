{% if area.pagination %}
<div class="{{ 'pager' | with_mods(area.kind) }}" data-ct-area="area-pager">
    {% if area.current_page == area.total_pages -%}
        <a class="pager__button pager__button--previous" href="{{ view.request | append_get_params(**area.pagination_info.previous_param) }}">
            {{- area.pagination_info.previous_label -}}
        </a>
    {% else -%}
        <a class="pager__button pager__button--next" href="{{ view.request | append_get_params(**area.pagination_info.next_param) }}">
            {{- area.pagination_info.next_label -}}
        </a>
    {% endif -%}
    <ul class="pager__pages">
        {% for num in area.pagination %}
        {% set page_info = area.page_info(num) %}
        <li class="pager__page{% if num == area.current_page %} pager__page--current{% endif %}">
            {%- if num == area.current_page -%}
                <span>{{ page_info.page_label }}</span>
            {%- elif num == 1 -%}
                <a href="{{ view.request.url | remove_get_params(page_info.remove_get_param) }}">{{ page_info.page_label }}</a>
            {%- elif num -%}
                <a href="{{ view.request | append_get_params(**page_info.append_get_param) }}">{{ page_info.page_label }}</a>
            {%- else -%}
                <span>…</span>
            {%- endif -%}
        </li>
        {% endfor %}
    </ul>
</div>
{% endif %}
