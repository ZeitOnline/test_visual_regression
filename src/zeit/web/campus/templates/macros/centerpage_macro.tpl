{% macro include_teaser_datetime(teaser, layout='', kind='') -%}
    {%- set time = get_delta_time_from_article(teaser) -%}
    {%- if time -%}
        <time class="{{ layout }}__datetime js-update-datetime" datetime="{{ teaser | release_date | format_date('iso8601') }}">
            {{ time }}
        </time>
    {%- endif %}
{%- endmacro %}
