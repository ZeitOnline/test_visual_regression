{#

Teaser template for large upright lead teasers

Parameters:
    format: to define type of leader
    shade: to define light/ dark shading
    supertitle: to define display of supertitle
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/abstract/abstract_leader_teaser_template.tpl" -%}

{% block format %}upright{% endblock %}
{% block shade %}dark{% endblock %}
{% block supertitle %}true{% endblock %}
