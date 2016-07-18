{#
Teaser template for fullwidth lead teaser
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-fullwidth{% endblock %}
{% block teaser_kicker %}{% endblock %}
{% block comments %}{% endblock %}

{% block teaser_image scoped %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.magazin:templates/inc/asset/image-fullwidth.tpl" %}
{% endblock %}
