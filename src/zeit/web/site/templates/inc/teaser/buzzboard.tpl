{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-buzzboard{% endblock %}
{% block meetrics %}{% endblock %} {# prevent tracking #}
{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_media_position_before_title %}
    {% if row == 0 %}
        {% set module_layout = self.layout() %}
        {% set media_caption_additional_class = 'figcaption--hidden' %}
        {% set href = teaser.uniqueId | create_url %}
        {% if teaser is column %}
            {% include "zeit.web.site:templates/inc/asset/image_buzzboard-column.tpl" ignore missing %}
        {% else %}
            {% include "zeit.web.site:templates/inc/asset/image_buzzboard.tpl" ignore missing %}
        {% endif %}
    {% endif %}
{% endblock %}

{% block teaser_container %}
    <span class="{{ self.layout() }}__metadata">
        {{ (teaser.score * module.score_factor) | round | pluralize(*module.score_pattern) }}
    </span>
{% endblock %}
