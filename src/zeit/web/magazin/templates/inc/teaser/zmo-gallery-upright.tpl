{#

Teaser template for gallery upright button teaser

Parameters:
    subtitle: to define display of subtitle
    format: to define type of button
    supertitle: to define display of supertitle
    icon: define display of optional asset icon
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-gallery-upright{% endblock %}
{% block icon %}
    <span class="icon-galerie-icon-white"></span>
{% endblock %}

{% block teaser_text %}{% endblock %}
