{% macro p(html, class) -%}
    <p class="{{ class }}">
        {{ html }}
    </p>
{%- endmacro %}

