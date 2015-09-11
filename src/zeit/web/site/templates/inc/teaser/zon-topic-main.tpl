{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% set ref_cp = area.referenced_cp %}
{% set topic_supertitle = area.supertitle or ref_cp.teaserSupertitle or ref_cp.supertitle %}
{% set readmore_url = area.read_more_url | create_url %}
{% if readmore_url is none and ref_cp is not none %}
    {% set readmore_url = ref_cp.uniqueId | create_url %}
{% endif %}
{% set readmore_text = area.read_more or 'Alles zum Thema' %}

{% block layout %}teaser-topic-main{% endblock %}

{% block teaser_media_position_before_title %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}_zop-topic.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
    <div class="{{ self.layout() }}__inner-helper">
{% endblock %}

{% block teaser_link %}
    {% if readmore_url %}
    <a class="{{ self.layout() }}__combined-link" title="{{ topic_supertitle | hide_none }} - {{ area.title | hide_none }}" href="{{ readmore_url }}">
        <span class="{{ self.layout() }}__kicker">{{ topic_supertitle | hide_none }}</span>
        <span class="{{ self.layout() }}__title">{{ area.title | hide_none }}</span>
    </a>
    {% endif %}
{% endblock %}

{% block teaser_container %}
{% endblock %}

{% block teaser_media_position_after_container %}
    </div>
{% endblock %}

{% block teaser_media_position_after_title %}
    {% if readmore_url %}
    <a href="{{ readmore_url }}">
        <span class="{{ self.layout() }}__readmore">{{ readmore_text }}</span>
    </a>
    {% endif %}
{% endblock %}
