{% macro include_teaser_datetime(teaser, layout_id='', modifier='') -%}
    <time class="{{ layout_id }}__datetime {{modifier}} js-update-datetime" datetime="{{ teaser | mod_date | format_date('iso8601') }}">{{ get_delta_time_from_article(teaser) | hide_none }}</time>
{%- endmacro %}

{% macro include_teaser_byline(teaser, layout_id='', modifier='') -%}
    <span class="{{ layout_id }}__byline {{modifier}}">{{ teaser | render_byline }}</span>
{%- endmacro %}

{% macro image_copyright(copyright, blockname) -%}
    {%- if copyright[0][1] -%}
        <a class="{{ blockname }}__link" href="{{ copyright[0][1] }}" target="_blank">
    {%- endif -%}
            <span class="{{ blockname }}__item">©&nbsp;{{ copyright[0][0] | replace('© ', '') }}</span>
    {%- if copyright[0][1] -%}
        </a>
    {%- endif -%}
{%- endmacro %}
