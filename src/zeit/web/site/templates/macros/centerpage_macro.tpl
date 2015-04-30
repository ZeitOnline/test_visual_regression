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
            {% include ['zeit.web.site:templates/inc/teaser/' + prefix + module | get_layout + '.html', 'zeit.web.site:templates/inc/teaser/default.html'] ignore missing %}
        {% endfor %}
    {% endif %}
{%- endmacro %}

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

{% macro playbutton(modifier, duration) %}
    <div class="video-text-playbutton video-text-playbutton--{{ modifier }}">
        <span class="video-text-playbutton__text video-text-playbutton__text--{{ modifier }}">Video ansehen</span><span class="video-text-playbutton__duration">{{ duration | hide_none }}</span>
    </div>
{% endmacro %}
