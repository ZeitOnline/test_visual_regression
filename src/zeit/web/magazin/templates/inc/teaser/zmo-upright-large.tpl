{#

Teaser template for large upright lead teasers

Parameters:
    layout: to define type of leader
    supertitle: to define display of supertitle
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/abstract/abstract_leader_teaser_template.tpl" -%}

{% block layout %}teaser-upright-large{% endblock %}
{% block supertitle %}true{% endblock %}
{% block teaser_text %}{% end block %}
