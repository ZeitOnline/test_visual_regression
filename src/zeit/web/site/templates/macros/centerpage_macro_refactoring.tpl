{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama with context %}

{% macro include_teaser_block(obj) -%}
    {% if obj -%}
        {% for teaser_block in obj -%}
            {% if teaser_block.layout -%}
                {{ include_teaser(teaser_block) }}
            {% endif %}
        {% endfor %}
    {% endif %}
{%- endmacro %}

{% macro include_teaser(teaser_block, prefix) -%}
    {% if prefix is not defined -%}
        {% set prefix = '' -%}
    {% endif %}

    {% if teaser_block -%}
        {% for teaser in teaser_block %}
            {% include ['zeit.web.site:templates/inc/teaser/' + prefix + teaser_block.layout.id + '.html', 'zeit.web.site:templates/inc/teaser/default.html'] ignore missing %}
        {% endfor %}
    {% endif %}
{%- endmacro %}

{% macro include_teaser_datetime(teaser, layout_id='', modifier='') -%}
    <time class="{{ layout_id }}__datetime {{modifier}} js-update-datetime" datetime="{{ teaser | mod_date | format_date('iso8601') }}">{{ get_delta_time(teaser) | hide_none }}</time>
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
