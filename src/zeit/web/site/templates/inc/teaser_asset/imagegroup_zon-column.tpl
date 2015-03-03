{%- extends "zeit.web.site:templates/inc/teaser_asset/imagegroup_refactoring.tpl" -%}

{% block image %}
    {% set image = get_column_image(teaser) %}
{% endblock %}
