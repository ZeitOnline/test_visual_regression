{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_image(module, teaser, variant_id='original') %}
{% set media_caption_additional_class = 'figcaption--hidden' %}

{# we don't need no figcaption for the kiosk #}
{% block media_caption %}{% endblock %}
