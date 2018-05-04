{% macro include_teaser_datetime(teaser, layout='', kind='') -%}
    {%- if kind == 'ranking' or kind == 'nextread' or kind.startswith('author') -%}
        {%- set time = teaser | mod_date | format_timedelta(days=3, absolute=True) | title -%}
    {%- elif kind == 'teaser-storystream' -%}
        {%- set time = teaser | mod_date | format_timedelta(days=3) -%}
    {%- else -%}
        {%- set time = get_delta_time_from_article(teaser) -%}
    {%- endif -%}
    {%- if time -%}
        {% if kind == 'nextread' or kind == 'teaser-storystream' %}
            <span class="{{ layout }}__dt">
                {{- time -}}
            </span>
        {% else %}
            <time class="{{ layout }}__datetime js-update-datetime" datetime="{{ teaser | mod_date | format_date('iso8601') }}">
                {{- time -}}
            </time>
        {% endif %}
    {%- endif %}
{%- endmacro %}
