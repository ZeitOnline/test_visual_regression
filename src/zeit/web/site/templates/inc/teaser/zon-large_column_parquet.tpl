{%- extends "zeit.web.site:templates/inc/teaser/abstract-column.tpl" -%}

{% block layout %}teaser-large-column-parquet{% endblock %}

{% block teaser_modifier %}{% if get_column_image(teaser) %}teaser-large-column-parquet--has-media{% endif %}{% endblock %}
