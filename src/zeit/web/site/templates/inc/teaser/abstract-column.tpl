{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-column{% endblock %}
{% block meetrics %}{% endblock %}

{# TODO: "get_column_image(teaser)" is also used in columnpic_zon-column.tpl . Should not be redundant. #}
{% block teaser_modifier %}{% if get_column_image(teaser) %}{{ self.layout() }}--has-media{% endif %}{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/columnpic_zon-column.tpl" %}
{% endblock %}

{% block teaser_journalistic_format %}
   <div class="{{ self.layout() }}__series-label">{{ teaser.serie.serienname }}</div>
{% endblock %}
{% block teaser_kicker %}
    <span class="{{ self.layout() }}__kicker">{{ teaser.teaserSupertitle }}</span>
{% endblock %}
{% block teaser_title %}
    <span class="{{ self.layout() }}__title">{{ teaser.teaserTitle }}</span>
{% endblock %}
