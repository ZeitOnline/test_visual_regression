{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-buzz{% endblock %}
{% block meetrics %}{% endblock %} {# prevent tracking #}
{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_container %}
    <span class="{{ self.layout() }}__metadata">
        {{ lama.use_svg_icon(module.icon, self.layout() + '__icon', view.package, a11y=false) }}
        {{ (adapt(teaser, 'zeit.web.core.interfaces.IReachData').score * module.score_factor) | round | pluralize(*module.score_pattern) }}
    </span>
{% endblock %}
