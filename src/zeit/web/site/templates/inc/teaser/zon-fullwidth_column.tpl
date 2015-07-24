{%- extends "zeit.web.site:templates/inc/teaser/abstract-column.tpl" -%}

{% block layout %}teaser-fullwidth-column{% endblock %}

{# TODO: "get_column_image(teaser)" is also used in columnpic_zon-column.tpl . Should not be redundant. #}
{% block teaser_modifier %}{% if get_column_image(teaser) %}teaser-fullwidth-column--has-media{% endif %}{% endblock %}
