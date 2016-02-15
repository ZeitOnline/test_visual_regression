{#
Teaser template for light fullwidth lead teaser
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-fullwidth{% endblock %}
{% block layout_shade %}teaser-fullwidth--light{% endblock %}
{% block teaser_kicker %}{% endblock %}
{% block comments %}{% endblock %}

{% block teaser_image scoped %}
    {% set media_caption_additional_class = 'figcaption--hidden' %}
    {% set module_layout = self.layout() %}
    {% set href = teaser | create_url %}
    {% include "zeit.web.magazin:templates/inc/asset/image-fullwidth.tpl" %}
{% endblock %}
