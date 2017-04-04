{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_image(block.printcover, fallback='default_packshot_diezeit') %}
{% set module_layout = 'volume-teaser' %}
{% set href = 'https://premium.zeit.de/abo/{}/{}/{}'.format(block.medium, block.year, block.issue) %}

{% block media_caption_content %}
    <a class="{{ module_layout }}__link" href="{{ href }}">
        {{ block.teaser_text }}
    </a>
{% endblock %}
