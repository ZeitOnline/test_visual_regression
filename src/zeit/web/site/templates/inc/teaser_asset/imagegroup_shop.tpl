{%- extends "zeit.web.site:templates/inc/asset/image.tpl" -%}

{% set image = get_image(module, teaser, fallback=False) %}
{% set media_caption_additional_class = 'figcaption--hidden' %}

{# we don't need no figcaption for the kiosk #}
{% block media_caption_content %}{% endblock %}
