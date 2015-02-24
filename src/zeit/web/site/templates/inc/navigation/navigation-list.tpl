<ul class="{{ nav_class }}{% if nav_class == 'primary-nav' %} primary-nav--js-no-overflow{% endif %}">
	{% for i in navigation -%}
	{% set section = navigation[i] %}
	<li class="{{ nav_class }}__item" data-id="{{ section.item_id }}"{% if section.has_children() %} data-feature="dropdown"{% endif %}>
		<a class="{{ nav_class }}__link{% if section.item_id in (view.ressort, view.sub_ressort) %} {{ nav_class }}__link--current{% endif %}" href="{{ section.href | translate_url }}">{{ section.text }}</a>
		{% if section.has_children() -%}
			{% include "zeit.web.site:templates/inc/navigation/navigation-section.tpl" %}
		{%- endif %}
	</li>
	{%- endfor %}
	{% if nav_class == 'primary-nav' %}
	{# copy all nav-sections to more-dropdown as well #}
	<li class="{{ nav_class }}__item" data-id="more-dropdown" data-feature="dropdown">
		<a class="{{ nav_class }}__link" href="#">mehr</a>
		{% include "zeit.web.site:templates/inc/navigation/navigation-more.tpl" %}
	</li>
	<li class="primary-nav__item primary-nav__item--featured">
		<a class="primary-nav__link" href="http://{{ view.request.host }}/zeit-magazin/index" id="hp.global.topnav.centerpages.zeitmagazin">ZEITmagazin</a>
	</li>
	{% endif %}
</ul>
