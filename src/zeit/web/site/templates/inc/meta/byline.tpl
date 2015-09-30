{%- macro text(obj) %}
    {{ obj }}
{%- endmacro -%}

{%- macro plain_author(obj) %}
    <span class="byline__author"><span itemprop="name">{{ obj.display_name }}</span></span>
{%- endmacro -%}

{%- macro linked_author(obj) %}
    <a href="{{ obj.uniqueId | create_url }}" class="byline__author" itemprop="url"><span itemprop="name">{{ obj.display_name }}</span></a>
{%- endmacro -%}

{%- macro csv(obj) -%}
    {%- for type, item in obj -%}
        {{ type | macro(item) }}
        {%- if not loop.last -%}
            ,
        {% endif -%}
    {%- endfor -%}
{%- endmacro -%}

{%- macro enum(obj) -%}
    {% for type, item in obj -%}
        {% if not loop.first and not loop.last -%}
            ,
        {%- elif loop.last and loop.length > 1 %}
            und
        {%- endif %}
        {{ type | macro(item) }}
    {%- endfor %}
{%- endmacro -%}

{% if (provides(byline, 'zeit.web.core.byline.IContentByline')
       or provides(byline, 'zeit.web.core.byline.ITeaserByline')) %}
{% for type, obj in byline -%}
    {{ type | macro(obj) }}
{%- endfor %}
{% endif %}
