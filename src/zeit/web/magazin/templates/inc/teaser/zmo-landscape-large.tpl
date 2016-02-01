{#

Teaser template for landscape large button teaser

Parameters:
    subtitle: to define display of subtitle
    format: to define type of button
    supertitle: to define display of supertitle
    icon: define display of optional asset icon
    image_class: define optional class for images
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}


{% block format %}large{% endblock %}
{% block image_class %}false{% endblock %}
