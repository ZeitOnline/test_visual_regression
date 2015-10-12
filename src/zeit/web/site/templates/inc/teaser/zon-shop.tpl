{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-gallery{% endblock %}

{% block teaser_media_position_before_title %}
	{% set module_layout = self.layout() %}

	{# OPTIMIZE: Figcaption would be better than this wrapper.
	   But JS fills the whole <figure> when loading an image.#}
	<div class="{{ self.layout() }}__figurewrapper">
		{% include "zeit.web.site:templates/inc/teaser_asset/imagegroup.tpl" %}
	</div>
{% endblock %}

{# Eliminate many default teaser blocks #}
{% block teaser_link %}{% endblock %}
{% block teaser_metadata_default %}{% endblock %}
{% block teaser_byline %}{% endblock %}
{% block teaser_journalistic_format %}{% endblock %}

