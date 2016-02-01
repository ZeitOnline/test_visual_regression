{#

Teaser template for large upright lead teasers

Parameters:
    layout: to define type of leader
    supertitle: to define display of supertitle
#}

{%- extends "zeit.web.magazin:templates/inc/teaser/abstract/abstract_leader_teaser_template.tpl" -%}

{% block layout %}teaser-upright-large{% endblock %}
{% block layout_asset %}teaser-upright-large__asset{% endblock %}
{% block layout_shade %}teaser-upright-large--dark{% endblock %}
{% block shade %}dark{% endblock %}
{% block supertitle %}true{% endblock %}
