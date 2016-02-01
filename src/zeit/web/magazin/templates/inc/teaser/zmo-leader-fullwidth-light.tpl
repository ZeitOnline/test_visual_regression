{#

Teaser template for light fullwidth lead teaser

Parameters:
    layout: to define type of leader
    supertitle: to define display of supertitle
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-fullwidth{% endblock %}
{% block layout_shade %}light{% endblock %}
{% block teaser_kicker %}{% endblock %}
{% block teaser_text %}{% endblock %}
{% block comments %}{% endblock %}
