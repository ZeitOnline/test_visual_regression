{%- extends "zeit.web.core:templates/inc/asset/image_linked.tpl" -%}

{% set href = teaser | create_url %}
{% set media_caption_additional_class = 'figcaption--hidden' %}

{% block media_link_title %}
    {{- teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title -}}
{% endblock %}
