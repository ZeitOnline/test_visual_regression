{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-buzz{% endblock %}
{% block meetrics %}{% endblock %}
{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_container %}
    <span class="{{ self.layout() }}__metadata">
        {{ lama.use_svg_icon(module.icon, self.layout() + '__icon', request) }}
        {{ (teaser.score * module.score_factor) | round | pluralize(*module.score_pattern) }}
    </span>
{% endblock %}
