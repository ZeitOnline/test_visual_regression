{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_image(teaser, variant_id='portrait', fallback=False, fill_color=None) %}

{% block media_caption %}{% endblock %}
