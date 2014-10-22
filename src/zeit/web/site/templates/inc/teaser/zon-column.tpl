{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_modifier %}teaser__column teaser--hasmedia{% endblock %}
{% block teaser_heading_modifier %}teaser__heading__small{% endblock %}

{% block teaser_media_position_before_title %}
    {% include "zeit.web.site:templates/inc/teaser_asset/"+
        teaser | auto_select_asset | block_type +
        "_zon-column.tpl" ignore missing with context %}
{% endblock %}

{% block teaser_link %}
<a class="teaser__combined-link" title="{{ teaser.serie }}: {{ teaser.teaserSupertitle }} - {{ teaser.teaserTitle }}" href="{{ teaser.uniqueId | translate_url }}">
    {% block teaser_kicker %}
    <span class="teaser__kicker">{{ teaser.serie }}: {{ teaser.teaserSupertitle }}</span>
    {% endblock %}
    {% block teaser_title %}
    <span class="teaser__title">{{ teaser.teaserTitle }}</span>
    {% endblock %}
</a>
{% endblock %}
