{%- extends "zeit.web.site:templates/inc/teaser/default_refactoring.tpl" -%}

{% block teaser_modifier %}teaser-column--smallmedia teaser-column--hasmedia{% endblock %}
{% block teaser_heading_modifier %}teaser-column__heading--padded{% endblock %}

{% block layout %}teaser-column{% endblock %}

{% block teaser_media_position_before_title %}
    {% set teaser_block_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "_zon-column.tpl" ignore missing with context %}
{% endblock %}

{% block teaser_link %}
<a class="teaser-column__combined-link teaser-column__combined-link--padded" title="{{ teaser.serie }}: {{ teaser.teaserSupertitle }} - {{ teaser.teaserTitle }}" href="{{ teaser.uniqueId | translate_url }}">
    {% block teaser_kicker %}
    <span class="teaser-column__kicker-container">
        <span class="teaser-column__series">{{ teaser.serie }}</span>
        <span class="teaser-column__kicker">{{ teaser.teaserSupertitle }}</span>
    </span>
    {% endblock %}
    {% block teaser_title %}
    <span class="teaser-column__title">{{ teaser.teaserTitle }}</span>
    {% endblock %}
</a>
{% endblock %}
