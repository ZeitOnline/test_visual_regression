{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_image(module, variant_id='original') %}

{# we don't need no figcaption for the kiosk #}
{% block media_caption %}{% endblock %}
