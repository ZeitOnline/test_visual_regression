{%- extends "zeit.web.site:templates/inc/teaser/abstract-column.tpl" -%}

{% block layout %}teaser-large-column{% endblock %}
{% block teaser_modifier %}{{ super() }} {{ self.layout() }}--parquet{% endblock %}
