{% set image = get_image(module, teaser, variant_id='super', fallback=False) %}
{% set href = teaser.url %}
{% set module_layout = 'nextread-advertisement' %}
{% set tracking_slug = 'articlebottom.publisher-nextread...' %}

<article class="{{ module_layout }}">
	<span class="{{ module_layout }}__label">{{ {'publisher': 'Verlagsangebot', 'advertisement': 'Anzeige'}.get(teaser.supertitle) }}</span>
	<div class="{{ module_layout }}__container-outer">
		<div class="{{ module_layout }}__container-inner">
			<h2 class="{{ module_layout }}__title">{{ teaser.title }}</h2>
			<p class="{{ module_layout }}__text">{{ teaser.text }}</p>
		        {% include "zeit.web.site:templates/inc/asset/image_nextread-advertisement.tpl" with context %}
			<a class="{{ module_layout }}__button" title="{{ teaser.title }}: {{ teaser.text }}" href="{{ teaser.url }}" style="background-color:#{{ teaser.button_color }}" data-id="{{ tracking_slug }}button">
				{{- teaser.button_text -}}
			</a>
		</div>
	</div>
</article>
