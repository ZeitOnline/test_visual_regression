{%- extends "zeit.web.arbeit:templates/inc/teaser/zar-quote.tpl" -%}

{% block layout %}teaser-quote{% endblock %}
{% block teaser_modifier %}{{ self.layout() | with_mods('red') }}{% endblock %}
{% block quotelink_class %}{{ ( self.layout() + '__quotelink' ) | with_mods('on-red') }}{% endblock %}
