{% extends "zeit.web.core:templates/inc/asset/image_linked.tpl" %}

{% set image = get_image(block.printcover,'original', fallback=True) %}
{% set module_layout = 'volume-teaser' %}
{% set href = 'https://premium.zeit.de/{}/{}/{}?wt_zmc=fix.int.zonpme.zede.rr.premium_intern.packshot.cover.cover&utm_medium=fix&utm_source=zede_zonpme_int&utm_campaign=rr&utm_content=webreader_packshot_cover_cover'.format(block.medium, block.year, block.issue) %}

{% block media_caption_content %}
    <a class="{{ module_layout }}__link" href="{{ href }}">
    {% if block.teaser_text %}
        {{ block.teaser_text }}
    {% else %}
        Dieser Artikel stammt aus der ZEIT Nr. {{ block.issue }}, {{ block.year }}. Lesen Sie diese Ausgabe als E-Paper, App und auf dem E-Reader.
    {% endif %}
    </a>
{% endblock %}
