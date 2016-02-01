{#

Teaser template for fullwidth lead teaser

Parameters:
    layout: to define type of leader
    shade: to define light/ dark shading
    supertitle: to define display of supertitle
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/abstract/abstract_leader_teaser_template.tpl" -%}

{% block layout %}teaser-fullwidth{% endblock %}
{% block layout_asset %}teaser-fullwidth__asset{% endblock %}
{% block layout_shade %}teaser-fullwidth--dark{% endblock %}
{% block shade %}dark{% endblock %}
{% block supertitle %}false{% endblock %}
