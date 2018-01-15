{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-classic{% endblock %}

{% block teaser_media_position_after_title %}
    {% set module_layout = self.layout() %}

    {% if toggles('responsive_image_leadteaser') and region_loop.first %}
        {% include "zeit.web.site:templates/inc/asset/picture_zon-classic.tpl" %}
    {% else %}
        {% include "zeit.web.site:templates/inc/asset/image_zon-classic.tpl" %}
    {% endif %}
{% endblock %}
