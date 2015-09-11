{%- extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" -%}

{% block layout %}teaser-small{% endblock %}
{% block meetrics %}{% endblock %}
{% block teaser_modifier %}{{ self.layout() }}--inhouse{% endblock %}
{% block teaser_label %}<span class="{{ self.layout() }}__label">Verlagsangebot</span>{% endblock %}
{% block teaser_kicker %}{% endblock %}
