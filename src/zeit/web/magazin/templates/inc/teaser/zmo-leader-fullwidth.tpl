{#
Teaser template for fullwidth lead teaser
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-fullwidth{% endblock %}
{% block teaser_kicker %}{% endblock %}
{% block comments %}{% endblock %}

{% block teaser_image scoped %}
    {% set media_caption_additional_class = 'figcaption--hidden' %}
    {% set module_layout = self.layout() %}
    {% set href = teaser | create_url %}
    {% include "zeit.web.magazin:templates/inc/asset/image-fullwidth.tpl" %}
{% endblock %}
