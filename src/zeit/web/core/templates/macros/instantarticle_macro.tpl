{% macro no_block(obj) %}{% endmacro %}

{% macro paragraph(html) -%}
    <p>
        {{ html | safe }}
    </p>
{%- endmacro %}
