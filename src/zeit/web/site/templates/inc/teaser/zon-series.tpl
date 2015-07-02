{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-series{% endblock %}

{% block teaser_media_position_before_title %}
    {% set module_layout = self.layout() %}
    {% include "zeit.web.site:templates/inc/teaser_asset/{}.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
{% endblock %}

{% block teaser_journalistic_format %}
	<div class="teaser-series__label">{{ teaser.serie.column and 'Kolumne' or 'Serie' }}: {{ teaser.serie.serienname }}</div>
{% endblock %}
