{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-topic-main{% endblock %}

{% block teaser_media_position_before_title %}
    {% set teaser_block_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "_zop-topic.tpl" ignore missing with context %}
    <div class="{{ self.layout() }}__inner-helper">
        <a href="{{ teaser.uniqueId | translate_url }}">
            <span class="{{ self.layout() }}__introduction">Thema im Überblick</span>
        </a>
{% endblock %}

{% block teaser_kicker %}
{% endblock %}

{% block teaser_container %}
{% endblock %}

{% block teaser_media_position_after_container %}
    </div>
{% endblock %}

{% block teaser_media_position_after_title %}
    {% if area.referenced_cp is not none %}
        {% set readmore_ref = area.referenced_cp.uniqueId | translate_url %}
    {% else %}
        {% set readmore_ref = teaser.uniqueId | translate_url %}
    {% endif %}
    <a href="{{ readmore_ref }}">
        <span class="{{ self.layout() }}__readmore">Alles zum Thema</span>
    </a>
{% endblock %}
