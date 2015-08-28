{%- extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" -%}

{% block layout %}teaser-small{% endblock %}
{% block teaser_modifier %}{{ self.layout() }}--verlag{% endblock %}
{% block teaser_label %}<label class="teaser-small__label">Verlagsangebot</label>{% endblock %}
{% block teaser_kicker %}{% endblock %}
