{#

Teaser template for nextread teasers in a minimal layout

Parameters:
    teaser_image: to define display of teaser image
    bg_image: to define display of background image
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/abstract/abstract_nextread_teaser_template.tpl" -%}

{% block teaser_image %}false{% endblock %}
{% block bg_image %}false{% endblock %}
