{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_image(content=obj, variant_id=obj.variant_name, fallback=False) or obj %}

{% block media_block %}photocluster__figure{% endblock %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
