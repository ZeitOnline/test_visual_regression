{%- extends "zeit.web.site:templates/inc/teaser/abstract-column.tpl" -%}

{% block layout %}teaser-small-column-parquet{% endblock %}

{% block teaser_media_position_before_title %}
	{# TODO: "get_column_image(teaser)" is also used in columnpic_zon-column.tpl . Should not be redundant. #}
	{% if get_column_image(teaser) %}
    	{% set module_layout = self.layout() %}
    	<div class="teaser-small-column-parquet__mediawrapper">
    		{% include "zeit.web.site:templates/inc/teaser_asset/columnpic_zon-column.tpl" %}
    	</div>
    {% endif %}
{% endblock %}
