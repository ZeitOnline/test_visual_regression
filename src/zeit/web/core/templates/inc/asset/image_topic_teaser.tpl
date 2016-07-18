{% if not is_topic_variant %}
    {%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}
{% else %}
    {%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}
{% endif %}

{% set media_caption_additional_class = 'figcaption--hidden' %}

{% block media_block %}{{ super() }} is-pixelperfect{% endblock %}

{% block media_link_title %}{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}{% endblock %}

{% block media_block_additional_data_attributes %}
    {%- set mobile_image = get_image(module, teaser, variant_id='wide') %}
    {%- if mobile_image %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}"
    {%- endif %}
{% endblock %}
