{% set items = navigation %}
{% set class = nav_class %}
{% set site_navigation_element = True if (class == 'primary-nav' or site_navigation_element) else False %}
<ul class="{{ class }}{% if class == 'primary-nav' %} primary-nav--js-no-overflow{% endif %}"
	{%- if class == 'primary-nav' %} itemscope itemtype="http://schema.org/SiteNavigationElement"{% endif %}>
{% for section in items.values() %}
	{% set id = section.item_id | pop_from_dotted_name -%}
    {% set section_id = id if id else section.item_id %}
	<li class="{{ class }}__item
		{%- if section.label %} {{ class }}__item--has-label{% endif %}" data-id="{{ id if id else section.item_id }}"
		{%- if section | length %} data-feature="dropdown"{% endif %}
		{%- if section.label %} data-label="{{ section.label }}"{% endif %}>
		<a class="{{ class }}__link{% if id in (view.ressort, view.sub_ressort) %} {{ class }}__link--current{% endif %}"
			href="{{ section.href | create_url }}"
			data-id="{{ section.item_id }}"
			{%- if site_navigation_element %} itemprop="url"{% endif %}>
			{%- if site_navigation_element -%}
				<span itemprop="name">{{ section.text }}</span>
			{%- else -%}
				{{- section.text -}}
			{%- endif -%}
		</a>
	{% if section | length -%}
		{%- set navigation = section -%}
		{%- set nav_class = "dropdown" -%}
		{% include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" %}
	{%- endif -%}
	</li>
{% endfor %}

{% if class == 'primary-nav' %}
	{# copy all nav-sections to more-dropdown as well #}
	<li class="{{ class }}__item" data-id="more-dropdown" data-feature="dropdown">
		<a class="{{ class }}__link" href="#">mehr</a>
		{%- set navigation = items -%}
		{%- set nav_class = "dropdown" -%}
		{%- set site_navigation_element = False -%}
		{% include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" %}
	</li>
	<li class="{{ class }}__item {{ class }}__item--featured">
		<a class="{{ class }}__link" itemprop="url" href="{{ request.route_url('home') }}zeit-magazin/index" data-id="topnav.mainnav.14..zeitmagazin">
			<span itemprop="name">ZEITmagazin</span>
		</a>
	</li>
{% endif %}
</ul>
