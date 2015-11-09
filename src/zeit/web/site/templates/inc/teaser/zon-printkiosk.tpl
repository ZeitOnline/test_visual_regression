{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-printkiosk{% endblock %}
{% block teaser_attributes %}data-type="teaser"{% endblock %}

{% block teaser_media_position_before_title %}
	{% set module_layout = self.layout() %}
	<div class="{{ module_layout }}__figurewrapper">
		{% include "zeit.web.site:templates/inc/teaser_asset/imagegroup_printkiosk.tpl" %}
	</div>
{% endblock %}

{% block teaser_container %}
    <p class="{{ self.layout() }}__title">{{ teaser.teaserTitle }}</p>
{% endblock %}

{# Eliminate many default teaser blocks #}
{% block teaser_journalistic_format %}{% endblock %}
{% block teaser_heading %}{% endblock %}

{# Disable Meetrics tracking #}
{% block meetrics %}{% endblock %}
