{% import 'zeit.web.core:templates/macros/layout_macro.tpl' as lama_core %}
{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block teaser_media_position_before_title %}
	{% set module_layout = self.layout() %}

	{# TODO: Figcaption would be better than this wrapper. #}
	<div class="zon-gallery__figurewrapper">
		{% include "zeit.web.site:templates/inc/teaser_asset/imagegroup.tpl" %}

		{{ lama_core.use_svg_icon('gallery', '{}__icon'.format(self.layout()), request) }}

		<small class="{{ self.layout() }}__counter">
			{{ teaser.keys() | list | length | pluralize('Keine Fotos', 'Ein Foto', '{} Fotos') }}
		</small>
	</div>
{% endblock %}

{# Eliminate default teaser metadata #}
{% block teaser_metadata_default %}{% endblock %}
{# Eliminate default teaser byline #}
{% block teaser_byline %}{% endblock %}
