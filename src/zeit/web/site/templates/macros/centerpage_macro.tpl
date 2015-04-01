{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama with context %}

{% macro include_module(obj) -%}
    {% if obj -%}
        {% for module in obj -%}
            {% if module.layout -%}
                {{ include_teaser(module) }}
            {% endif %}
        {% endfor %}
    {% endif %}
{%- endmacro %}

{% macro include_teaser(module, prefix) -%}
    {% if prefix is not defined -%}
        {% set prefix = '' -%}
    {% endif %}

    {% if module -%}
        {% for teaser in module %}
            {% include ['zeit.web.site:templates/inc/teaser/' + prefix + module.layout.id + '.html', 'zeit.web.site:templates/inc/teaser/default.html'] ignore missing %}
        {% endfor %}
    {% endif %}
{%- endmacro %}

{% macro include_teaser_datetime(teaser) -%}
    <time class="teaser__datetime" datetime="{{ teaser | mod_date | strftime('%Y-%m-%d %H:%M') | hide_none }}">{{ get_delta_time(teaser) | hide_none }}</time>
{%- endmacro %}

{% macro include_teaser_commentcount(teaser) -%}
    <a class="teaser__commentcount" href="{{ teaser.uniqueId | translate_url }}#comments" title="9 Kommentare">9 Kommentare</a>
{%- endmacro %}

{% macro include_teaser_byline(teaser, modifier='') -%}
    <span class="teaser__byline {{modifier}}">{{ teaser | render_byline }}</span>
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
