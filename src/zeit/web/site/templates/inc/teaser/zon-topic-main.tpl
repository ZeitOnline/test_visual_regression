{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% set ref_cp = area.referenced_cp %}
{% set topic_supertitle = area.supertitle or ref_cp.teaserSupertitle or ref_cp.supertitle %}

{% block layout %}teaser-topic-main{% endblock %}

{% block teaser_media_position_before_title %}
    {% set teaser_block_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "_zop-topic.tpl" ignore missing with context %}
    <div class="{{ self.layout() }}__inner-helper">
{% endblock %}

{% block teaser_link %}
    <a class="{{ self.layout() }}__combined-link" title="{{ topic_supertitle | hide_none }} - {{ area.title | hide_none }}" href="{{ ref_cp.uniqueId | translate_url }}">
        <span class="{{ self.layout() }}__kicker">{{ topic_supertitle | hide_none }}</span>
        <span class="{{ self.layout() }}__title">{{ area.title | hide_none }}</span>
    </a>
{% endblock %}

{% block teaser_container %}
{% endblock %}

{% block teaser_media_position_after_container %}
    </div>
{% endblock %}

{% block teaser_media_position_after_title %}
    {% if ref_cp is not none %}
        {% set readmore_ref = ref_cp.uniqueId | translate_url %}
    {% else %}
        {% set readmore_ref = teaser.uniqueId | translate_url %}
    {% endif %}
    <a href="{{ readmore_ref }}">
        <span class="{{ self.layout() }}__readmore">Alles zum Thema</span>
    </a>
{% endblock %}
