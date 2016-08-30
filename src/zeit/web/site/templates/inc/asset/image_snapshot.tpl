{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set image = get_image(teaser, name='content', variant_id='wide', fallback=False) %}
{% set href = module.read_more_url %}
{% block media_caption_class %}{{ module_layout }}{% endblock %}
{% block media_link_title %}{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}{% endblock %}

{% block media_caption_content %}
    <span class="{{ module_layout }}__text" itemprop="caption">{{ image.caption | trim }}</span>
    {{ super() }}
{% endblock %}
