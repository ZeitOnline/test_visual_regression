{% set blockname = 'nextread-advertisement' %}

{% macro get_label(xml_label) -%}
	{% if xml_label == 'publisher' %}
		Verlagsangebot
	{% elif xml_label == 'advertisement' %}
		Anzeige
	{% else %}{% endif %}
{%- endmacro %}

<article class="{{ blockname }}">
	<div class="{{ blockname }}__container-outer">
		<span class="{{ blockname }}__label">{{ get_label(teaser.supertitle) }}</span>
		<div class="{{ blockname }}__container-inner">
			<h2 class="{{ blockname }}__title">{{ teaser.title }}</h2>
			<p class="{{ blockname }}__text">{{ teaser.text }}</p>

	        <figure class="{{ blockname }}__media">
	            <a href="{{ teaser.url }}" title="{{ teaser.title }}">
	                <!-- img class="print-box__media-item" src="{{ teaser.image | default_image_url('wide') }}" -->
	                <!-- img class="print-box__media-item" src="{{ teaser.image | closest_substitute_image('default') }}" -->
	                <img class="{{ blockname }}__media-item" src="http://127.0.0.1:9090/angebote/verlagsnextread/images/shop_unser-geheimnisvolles-ich/produktbild_unser-geheimnisvolles-ich_720x600.jpg" />
	            </a>
	        </figure>

			{#
	        {% set image = teaser | get_image(teaser) %}
	        {{ image | default_image_url() }}
	        {% set href = teaser.uniqueId | create_url %}
	        {% include "zeit.web.site:templates/inc/linked-image.tpl" %}
	        #}

			{#
	        {%- extends "zeit.web.site:templates/inc/linked-image.tpl" -%}
			{% set image = module | get_image(teaser) %}
			{% set href = teaser.uniqueId | create_url %}
			#}

			<a class="{{ blockname }}__button" title="{{ teaser.title }}: {{ teaser.text }}" href="{{ teaser.url }}" style="background-color:#{{ teaser.button_color }}">
				{{ teaser.button_text }}
			</a>
		</div>
	</div>
</article>
