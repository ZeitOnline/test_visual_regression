{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-buzzboard{% endblock %}
{% block meetrics %}{% endblock %}
{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_media_position_before_title %}
	{% if row == 0 %}
		{% set module_layout = self.layout() %}
		{% include "zeit.web.site:templates/inc/teaser_asset/{}_buzzboard.tpl".format(teaser | auto_select_asset | block_type) ignore missing %}
	{% endif %}
{% endblock %}

{% block teaser_container %}
	<span class="{{ self.layout() }}__metadata">
		{{ (teaser.score * module.score_factor) | round | pluralize(*module.score_pattern) }}
	</span>
{% endblock %}
