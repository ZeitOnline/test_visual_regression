{% set module_layout = 'nextread-advertisement' %}

{% macro get_label(xml_label) -%}
	{% if xml_label == 'publisher' %}
		Verlagsangebot
	{% elif xml_label == 'advertisement' %}
		Anzeige
	{% else %}{% endif %}
{%- endmacro %}

<article class="{{ module_layout }}">
	<div class="{{ module_layout }}__container-outer">
		<span class="{{ module_layout }}__label">{{ get_label(teaser.supertitle) }}</span>
		<div class="{{ module_layout }}__container-inner">
			<h2 class="{{ module_layout }}__title">{{ teaser.title }}</h2>
			<p class="{{ module_layout }}__text">{{ teaser.text }}</p>

			{% set image = get_image(module, teaser, variant_id='super') %}
	        {% set href = teaser.url %}
	        {% set tracking_slug = 'articlebottom.publisher-nextread...' %}

	        {% include "zeit.web.site:templates/inc/linked-image.tpl" %}

			<a class="{{ module_layout }}__button" title="{{ teaser.title }}: {{ teaser.text }}" href="{{ teaser.url }}" style="background-color:#{{ teaser.button_color }}" data-id="{{ tracking_slug }}button">
				{{ teaser.button_text }}
			</a>
		</div>
	</div>
</article>
