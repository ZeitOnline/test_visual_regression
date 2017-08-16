{%- extends "zeit.web.arbeit:templates/inc/teaser/zar-quote.tpl" -%}

{% block layout %}teaser-quote{% endblock %}
{% block teaser_modifier %}{{ self.layout() }}--yellow{% endblock %}
