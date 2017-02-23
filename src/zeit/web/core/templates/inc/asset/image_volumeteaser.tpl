{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_image(block.printcover, fallback='default_packshot_diezeit') %}
{% set module_layout = 'volume-teaser' %}
{% set href = 'https://premium.zeit.de/abo/{}/{}/{}'.format(block.medium, block.year, block.issue) %}

{% block media_caption_content %}
    <a class="{{ module_layout }}__link" href="{{ href }}">
    {% if block.teaser_text %}
        {{ block.teaser_text }}
    {% else %}
        Dieser Artikel stammt aus der ZEIT Nr. {{ block.issue }}/{{ block.year }}. Hier können Sie die gesamte Ausgabe lesen.
    {% endif %}
    </a>
{% endblock %}
