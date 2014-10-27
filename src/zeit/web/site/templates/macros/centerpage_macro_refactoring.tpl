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

{% macro include_teaser_datetime(teaser, layout='', modifier='') -%}
    <time class="teaser-{{ layout }}__datetime {{modifier}}" datetime="{{ teaser | mod_date |strftime('%Y-%m-%d %H:%M') }}">{{ get_delta_time(teaser) | hide_none }}</time>
{%- endmacro %}

{% macro include_teaser_commentcount(teaser, layout='', modifier='') -%}
    <a class="teaser-{{ layout }}__commentcount {{modifier}}" href="{{ teaser.uniqueId | translate_url }}#comments" title="9 Kommentare">9 Kommentare</a>
{%- endmacro %}

{% macro include_teaser_byline(teaser, layout='', modifier='') -%}
    <span class="teaser-{{ layout }}__byline {{modifier}}">{{ teaser | render_byline }}</span>
{%- endmacro %}
