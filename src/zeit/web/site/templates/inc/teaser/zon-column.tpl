{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_modifier %}teaser-column--smallmedia teaser-column--hasmedia{% endblock %}
{% block teaser_heading_modifier %}teaser-column__heading--padded{% endblock %}

{% block layout %}teaser-column{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/columnpic_zon-column.tpl" %}
{% endblock %}

{% block teaser_link %}
<a class="teaser-column__combined-link teaser-column__combined-link--padded" title="{{ teaser.serie.serienname }}: {{ teaser.teaserSupertitle }} - {{ teaser.teaserTitle }}" href="{{ teaser.uniqueId | create_url }}">
    {% block teaser_kicker %}
    <span class="teaser-column__kicker-container">
        <span class="teaser-column__series">{{ teaser.serie.serienname }}</span>
        <span class="teaser-column__kicker">{{ teaser.teaserSupertitle }}</span>
    </span>
    {% endblock %}
    {% block teaser_title %}
    <span class="teaser-column__title">{{ teaser.teaserTitle }}</span>
    {% endblock %}
</a>
{% endblock %}
