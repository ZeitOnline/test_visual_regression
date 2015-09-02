{% set blockname = 'nextread-advertisement' %}

{% macro get_label(xml_label) -%}
	{% if xml_label == 'publisher' %}
		Verlagsangebot
	{% elif xml_label == 'advertisement' %}
		Anzeige
	{% else %}{% endif %}
{%- endmacro %}

<article class="{{ blockname }}">
	<span class="{{ blockname }}__label">{{ get_label(teaser.supertitle) }}</span>
	<div class="{{ blockname }}__container">
		<h2 class="{{ blockname }}__title">{{ teaser.title }}</h2>
		<p class="{{ blockname }}__text">{{ teaser.text }}</p>

		<div class="{{ blockname }}__image-container">
			{{ teaser.image }}

		{#
        <figure class="print-box__media">
            <a href="{{ teaser.url }}?wt_zmc=cross.int.zonpme.zeitde.angebbox.probe.bildtext.cover.cover&amp;utm_medium=cross&amp;utm_source=zeitde_zonpme_int&amp;utm_campaign=angebbox&amp;utm_content=probe_bildtext_cover_cover" title="{{ teaser.title }}" data-id="{{ teaser_position }}.angebots-box.image">
                <img class="print-box__media-item" src="{{ module.image | default_image_url('zon-printbox') }}">
            </a>
        </figure>
        #}

		{#
        {%- extends "zeit.web.site:templates/inc/linked-image.tpl" -%}
		{% set image = module | get_image(teaser) %}
		{% set href = teaser.uniqueId | create_url %}
		#}

		</div>

		<a class="{{ blockname }}__button" title="{{ teaser.title }}: {{ teaser.text }}" href="{{ teaser.url }}" style="background-color:{{ teaser.button_color }}">
			{{ teaser.button_text }}
		</a>
	</div>
</article>
