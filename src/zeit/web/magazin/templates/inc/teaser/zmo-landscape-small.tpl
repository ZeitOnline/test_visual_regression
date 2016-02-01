{#

Teaser template for landscape small button teaser

Parameters:
    subtitle: to define display of subtitle
    format: to define type of button
    supertitle: to define display of supertitle
    icon: define display of optional asset icon
    image_class: define optional class for images
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}


{% block format %}small{% endblock %}
{% block image_class %}false{% endblock %}
