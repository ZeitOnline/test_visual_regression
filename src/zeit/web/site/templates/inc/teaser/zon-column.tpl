{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{# TODO: "get_column_image(teaser)" is also used in columnpic_zon-column.tpl . Should not be redundant. #}
{% block teaser_modifier %}{% if get_column_image(teaser) %}teaser-column--hasmedia{% endif %}{% endblock %}


{% block layout %}teaser-column{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/columnpic_zon-column.tpl" %}
{% endblock %}

{% block teaser_journalistic_format %}
   <span class="teaser-column__series">{{ teaser.serie.serienname }}</span>
{% endblock %}
{% block teaser_kicker %}
    <span class="teaser-column__kicker">{{ teaser.teaserSupertitle }}</span>
{% endblock %}
{% block teaser_title %}
    <span class="teaser-column__title">{{ teaser.teaserTitle }}</span>
{% endblock %}
