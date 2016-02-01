{#

Teaser template for fullwidth lead teaser

Parameters:
    layout: to define type of leader
    shade: to define light/ dark shading
    supertitle: to define display of supertitle
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-fullwidth{% endblock %}
{% block teaser_kicker %}{% endblock %}
{% block teaser_text %}{% endblock %}
{% block comments %}{% endblock %}
