{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_modifier %}teaser__column teaser--hasmedia{% endblock %}
{% block teaser_heading_modifier %}teaser__heading--bordered{% endblock %}

{% block teaser_media_position_before_title %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "_zon-column.tpl" ignore missing with context %}
{% endblock %}

{% block teaser_link %}
<a class="teaser__combined-link teaser__combined-link--padded" title="{{ teaser.serie }}: {{ teaser.teaserSupertitle }} - {{ teaser.teaserTitle }}" href="{{ teaser.uniqueId | translate_url }}">
    {% block teaser_kicker %}
    <span class="teaser__column__kicker-container">
        <span class="teaser__column__series">{{ teaser.serie }}</span>
        <span class="teaser__column__kicker">{{ teaser.teaserSupertitle }}</span>
    </span>
    {% endblock %}
    {% block teaser_title %}
    <span class="teaser__column__title">{{ teaser.teaserTitle }}</span>
    {% endblock %}
</a>
{% endblock %}

{% block teaser_byline %}
    {{ cp.include_teaser_byline(teaser, 'teaser__byline--column') }}
{% endblock %}

{% block teaser_metadata_default %}
<div class="teaser__column__metadata">
    {% block teaser_datetime %}
        {{ cp.include_teaser_datetime(teaser) }}
    {% endblock %}
    {% block teaser_commentcount%}
        {{ cp.include_teaser_commentcount(teaser) }}
    {% endblock %}
</div>
{% endblock %}
