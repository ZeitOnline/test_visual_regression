{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-shop{% endblock %}
{% block teaser_attributes %}data-type="teaser"{% endblock %}

{% block teaser_media_position_before_title %}
	{% set module_layout = self.layout() %}

	{# OPTIMIZE: Figcaption would be better than this wrapper.
	   But JS fills the whole <figure> when loading an image.#}
	<div class="{{ self.layout() }}__figurewrapper">
		{% include "zeit.web.site:templates/inc/asset/image_teaser.tpl" %}
	</div>
{% endblock %}

{% block teaser_text %}
	{% set module_layout = self.layout() %}
	{% set href = teaser | create_url %}
	<a href="{{ href }}">
		{{ super() }}
	</a>
{% endblock %}

{# Eliminate many default teaser blocks #}
{% block teaser_journalistic_format %}{% endblock %}
{% block teaser_heading %}{% endblock %}
{% block teaser_metadata_default %}{% endblock %}

{# Disable Meetrics tracking #}
{% block meetrics %}{% endblock %}
