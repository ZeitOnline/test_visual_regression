{% extends "zeit.web.core:templates/inc/asset/image.tpl" %}

{% set image = get_image(volume.covers['printcover'],variant_id='original', fallback=True) %}
{% set href = 'https://zeit.de/{0}/{1:02d}/index?wt_params=foo42'.format(volume.year, volume.volume) %}

{% block media_caption_content %}
    <p class="{{ module_layout }}__issue">{{ '%02d' % volume.volume }}/{{ volume.year }}</p>
    <a class="{{ module_layout }}__link" href="{{ href }}">Jetzt lesen</a>
{% endblock %}
