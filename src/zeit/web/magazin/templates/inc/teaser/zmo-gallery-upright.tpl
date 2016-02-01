{#

Teaser template for gallery upright button teaser

Parameters:
    subtitle: to define display of subtitle
    format: to define type of button
    supertitle: to define display of supertitle
    icon: define display of optional asset icon
    image_class: define optional class for images
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/abstract/abstract_button_teaser_template.tpl" -%}

{% block subtitle %}false{% endblock %}
{% block format %}gallery{% endblock %}
{% block supertitle %}true{% endblock %}
{% block image_class %}false{% endblock %}

{% block icon %}
    <span class="icon-galerie-icon-white"></span>
{% endblock %}
