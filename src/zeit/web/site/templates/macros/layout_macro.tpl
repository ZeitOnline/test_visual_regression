{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama_core with context%}

{% macro show_informative_ad(view, show_only_when_fullwidth=false) -%}
    {% set is_fullwidth = view.area_fullwidth|length %}
    {% if show_only_when_fullwidth and is_fullwidth != 0 %}
        {{ lama_core.adplace(view.banner(7), view) }}
    {% elif not show_only_when_fullwidth and not is_fullwidth %}
        {{ lama_core.adplace(view.banner(7), view) }}
    {%- endif %}
{%- endmacro %}
