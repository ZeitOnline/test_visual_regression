{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama_core with context %}

{% macro adplace_desktop(item) -%}
    {{ lama_core.adplace(item, view) }}
{%- endmacro %}
