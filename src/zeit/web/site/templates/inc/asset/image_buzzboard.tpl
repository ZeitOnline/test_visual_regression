{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set image = None %}
{% set modifier = None %}
{% set href = teaser | create_url | append_campaign_params %}
{% set media_caption_additional_class = 'figcaption--hidden' %}

{% if teaser is column %}
    {% set image = get_image(teaser, name='author', fallback=False) %}
    {% set modifier = 'column' %}
{% endif %}

{% if not image %}
    {% set image = get_image(teaser, variant_id='wide', fallback=True) %}
    {% set modifier = None %}
{% endif %}

{% block media_block %}
    {{ super() | with_mods(modifier, 'duplicate' if image.path in view.buzzboard_images(image.path)) }}
{% endblock %}
{% block media_block_helper %}
    {{ super() | with_mods(modifier) }}
{% endblock %}

{% block media_link_title %}{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}{% endblock %}
