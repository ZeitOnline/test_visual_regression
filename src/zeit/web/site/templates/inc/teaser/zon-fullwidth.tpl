{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-fullwidth{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}

    {% if toggles('responsive_image_leadteaser') and region_loop.first %}
        {% include "zeit.web.site:templates/inc/asset/picture_zon-fullwidth.tpl" %}
    {% else %}
        {% include "zeit.web.site:templates/inc/asset/image_zon-fullwidth.tpl" %}
    {% endif %}
{% endblock %}
