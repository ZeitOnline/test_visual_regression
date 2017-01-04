{% if area.pagination %}
<div class="{{ 'pager' | with_mods(area.kind) }}" data-ct-area="area-pager" data-ct-row="{{ 'page_%s_of_%s' | format(area.current_page, area.total_pages) }}" data-ct-column="false">
    {% if area.current_page == area.total_pages -%}
        <a class="pager__button pager__button--previous" href="{{ area.page_info(area.current_page - 1).url }}">
            {{- area.pagination_info.previous_label -}}
        </a>
    {% else -%}
        <a class="pager__button pager__button--next" href="{{ area.page_info(area.current_page + 1).url }}">
            {{- area.pagination_info.next_label -}}
        </a>
    {% endif -%}
    <ul class="pager__pages">
        {% for num in area.pagination %}
        {% set page_info = area.page_info(num) %}
        <li class="pager__page{% if num == area.current_page %} pager__page--current{% endif %}">
            {%- if num == area.current_page -%}
                <span>{{ page_info.label }}</span>
            {%- elif num -%}
                <a href="{{ page_info.url }}">{{ page_info.label }}</a>
            {%- else -%}
                <span>…</span>
            {%- endif -%}
        </li>
        {% endfor %}
    </ul>
</div>
{% endif %}
