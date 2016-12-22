{% if not is_topic_variant %}
    {%- extends "zeit.web.core:templates/inc/asset/image.tpl" -%}
{% else %}
    {%- set tracking_slug = '{}.{}.1.teaser-topic-wide.'.format(area.kind, region_loop.index) -%}
    {%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}
{% endif %}

{% set media_caption_additional_class = 'figcaption--hidden' %}

{% block media_block %}{{ super() }} is-pixelperfect{% endblock %}

{% block media_link_title %}{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}{% endblock %}

{% block media_block_additional_data_attributes %}
    {%- require mobile_image = get_image(teaser, variant_id='portrait', fallback=True) %}
    data-mobile-src="{{ request.image_host + mobile_image.path }}" data-mobile-ratio="{{ mobile_image.ratio }}"
    {%- endrequire %}
{% endblock %}
