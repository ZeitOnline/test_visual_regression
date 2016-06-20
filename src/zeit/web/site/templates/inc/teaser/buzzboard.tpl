{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-buzzboard{% endblock %}
{% block meetrics %}{% endblock %} {# prevent tracking #}
{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_media_position_before_title %}
    {% if row == 0 %}
        {% set module_layout = self.layout() %}
        {% if teaser is column %}
            {% set media_block_additional_class = 'teaser-buzzboard__media--column' %}
            {% set media_container_additional_class = 'teaser-buzzboard__media-container--column' %}
            {% include "zeit.web.site:templates/inc/asset/image_zon-column.tpl" %}
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
