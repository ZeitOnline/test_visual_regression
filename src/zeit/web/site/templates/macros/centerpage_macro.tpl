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

{% macro include_teaser_datetime() -%}
    <time class="teaser__datetime" datetime="2014-09-11 13:16">vor 1 Minute</time>
{%- endmacro %}

{% macro include_teaser_commentcount(teaser) -%}
    <a class="teaser__commentcount" href="{{ teaser.uniqueId | translate_url }}#comments" title="9 Kommentare">9 Kommentare</a>
{%- endmacro %}

{% macro include_teaser_byline(teaser, modifier='') -%}
    <span class="teaser__byline {{modifier}}">ToDo: Insert byline here</span>
{%- endmacro %}
