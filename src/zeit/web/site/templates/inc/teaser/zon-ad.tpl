{%- extends "zeit.web.site:templates/inc/teaser/zon-inhouse.tpl" -%}

{% block teaser_modifier %}{{ self.layout() }}--ad{% endblock %}
{% block teaser_label %}<span class="{{ self.layout() }}__label">Anzeige</span>{% endblock %}
