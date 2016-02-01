{#

Teaser template for mtb square button teaser

Parameters:
    subtitle: to define display of subtitle
    format: to define type of button
    supertitle: to define display of supertitle
    icon: define display of optional asset icon
    image_class: define optional class for images
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block teaser_text %}{% endblock %}
{% block format %}mtb{% endblock %}
{% block image_class %}mtb__teaser__image{% endblock %}
