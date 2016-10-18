{%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}

{% set image = get_image(obj, fallback=False) %}
{% set module_layout = 'photocluster' %}
{% set media_block_additional_class = self.media_block() ~ ['--small', '--large'] | random %}
{% set media_caption_additional_class = 'figcaption--hidden' %}
{% block media_caption_class %}{{ module_layout }}{% endblock %}
