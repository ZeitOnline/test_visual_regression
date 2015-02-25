{%- set items = navigation -%}
{%- set class = nav_class -%}
<ul class="{{ class }}{% if class == 'primary-nav' %} primary-nav--js-no-overflow{% endif %}">
	{% for i in items -%}
	{% set section = items[i] %}
	<li class="{{ class }}__item" data-id="{{ section.item_id }}"{% if section.has_children() %} data-feature="dropdown"{% endif %}>
		<a class="{{ class }}__link{% if section.item_id in (view.ressort, view.sub_ressort) %} {{ class }}__link--current{% endif %}" href="{{ section.href | translate_url }}">{{ section.text }}</a>
		{% if section.has_children() -%}
			{%- set navigation = section -%}
			{%- set nav_class = "dropdown" -%}
			{% include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" %}
		{%- endif %}
	</li>
	{% endfor %}
	{% if class == 'primary-nav' %}
	{# copy all nav-sections to more-dropdown as well #}
	<li class="{{ class }}__item" data-id="more-dropdown" data-feature="dropdown">
		<a class="{{ class }}__link" href="#">mehr</a>
		{%- set navigation = items -%}
		{%- set nav_class = "dropdown" -%}
		{% include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" %}
	</li>
	<li class="{{ class }}__item {{ class }}__item--featured">
		<a class="{{ class }}__link" href="http://{{ view.request.host }}/zeit-magazin/index" id="hp.global.topnav.centerpages.zeitmagazin">ZEITmagazin</a>
	</li>
	{% endif %}
</ul>
