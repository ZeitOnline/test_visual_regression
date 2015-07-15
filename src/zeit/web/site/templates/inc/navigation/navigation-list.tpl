{%- set items = navigation -%}
{%- set class = nav_class -%}
<ul class="{{ class }}{% if class == 'primary-nav' %} primary-nav--js-no-overflow{% endif %}"
{% if class == 'primary-nav' %}
itemscope="itemscope"
itemtype="http://schema.org/SiteNavigationElement"
{% endif %}>
	{% for i in items -%}
	{% set section = items[i] %}
    {% set id = section.item_id | getIdFromWebtrekkString %}
	<li class="{{ class }}__item" data-id="{{ id if id else section.item_id }}" {% if section.has_children() %} data-feature="dropdown"{% endif %}>
		<a class="{{ class }}__link{% if id in (view.ressort,
        view.sub_ressort) %} {{ class }}__link--current{% endif %}" href="{{
        section.href | create_url }}" itemprop="url" data-id="{{ section.item_id }}"><span itemprop="name">{{
        section.text }}</span></a>
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
		<a class="{{ class }}__link" itemprop="url" href="http://{{
        view.request.host }}/zeit-magazin/index"
        data-id="topnav.mainnav.14..zeitmagazin"><span
        itemprop="name">ZEITmagazin</span></a>
	</li>
	{% endif %}
</ul>
