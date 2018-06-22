{%- extends "zeit.web.magazin:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-buzzboard{% endblock %}
{% block teaser_video %}{% endblock %}
{% block teaser_image %}{% endblock %}
{% block comments %}{% endblock %}
{% block teaser_text %}
    <span class="teaser-buzzboard__metadata">
       {{- (adapt(teaser, 'zeit.web.core.interfaces.IReachData').score * module.score_factor) | round | pluralize(*module.score_pattern) -}}
    </span>
{% endblock %}
