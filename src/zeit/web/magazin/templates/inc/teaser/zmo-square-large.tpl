{#

Teaser template for large square lead teasers

Parameters:
    layout: to define type of leader
    shade: to define light/ dark shading
    supertitle: to define display of supertitle
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-square-large{% endblock %}
{% block supertitle %}true{% endblock %}
{% block teaser_text %}{% endblock %}
