{%- extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" -%}

{% block teaser_modifier %}teaser__series teaser__series--smallmedia teaser__series--hasmedia{% endblock %}
{% block teaser_heading_modifier %}teaser__heading__small{% endblock %}

{% block teaser_media_position_before_title %}
    <div class="teaser__label teaser__label--series">Serie: {{teaser.serie}}</div>
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "_zon-serie-thumbnail.tpl" ignore missing with context %}
{% endblock %}

{% block teaser_kicker %}
    <span class="teaser__series__kicker">{{ teaser.teaserSupertitle }}</span>
{% endblock %}

{% block teaser_title %}
    <span class="teaser__series__title">{{ teaser.teaserTitle }}</span>
{% endblock %}

{% block teaser_text %}
    <p class="teaser__series__text">{{ teaser.teaserText }}{% block teaser_byline_inner %}{% endblock %}</p>
{% endblock %}

{% block teaser_byline %}
    {{ cp.include_teaser_byline(teaser, 'teaser__series__byline') }}
{% endblock %}

{% block teaser_metadata_default %}
<div class="teaser__series__metadata">
    {% block teaser_datetime %}
        {{ cp.include_teaser_datetime(teaser) }}
    {% endblock %}
    {% block teaser_commentcount%}
        {{ cp.include_teaser_commentcount(teaser) }}
    {% endblock %}
</div>
{% endblock %}
