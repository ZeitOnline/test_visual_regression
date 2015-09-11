{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-gallery{% endblock %}
{% block teaser_journalistic_format %}{% endblock %}
{% block meetrics %}{% endblock %}

{% block teaser_media_position_before_title %}
	{% set module_layout = self.layout() %}

	{# OPTIMIZE: Figcaption would be better than this wrapper.
	   But JS fills the whole <figure> when loading an image.#}
	<div class="{{ self.layout() }}__figurewrapper">
		{% include "zeit.web.site:templates/inc/teaser_asset/imagegroup.tpl" %}

		{{ lama.use_svg_icon('gallery', '{}__icon'.format(self.layout()), request) }}

		<small class="{{ self.layout() }}__counter">
			{{ teaser.keys() | list | length | pluralize('Keine Fotos', 'Ein Foto', '{} Fotos') }}
		</small>
	</div>
{% endblock %}

{# Eliminate default teaser metadata #}
{% block teaser_metadata_default %}{% endblock %}
{# Eliminate default teaser byline #}
{% block teaser_byline %}{% endblock %}
