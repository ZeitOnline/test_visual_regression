{%- macro text(obj) %}
    {{ obj }}
{%- endmacro -%}

{%- macro plain_author(obj) %}
    <span itemprop="author" itemscope itemtype="http://schema.org/Person"><span class="byline__author" itemprop="name">
        {{- obj.display_name -}}
    </span></span>
{%- endmacro -%}

{%- macro linked_author(obj) %}
    <span itemprop="author" itemscope itemtype="http://schema.org/Person"><a href="{{ obj.uniqueId | create_url }}" itemprop="url"><span class="byline__author" itemprop="name">
        {{- obj.display_name -}}
    </span></a></span>
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

{%- for type, obj in byline -%}
    {{ type | macro(obj) }}
{%- endfor %}
