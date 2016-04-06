{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

<div class="main_nav">
	<!-- logo -->
	<div id="publisher" itemprop="publisher" itemscope itemtype="http://schema.org/Organization" class="logo_bar">
		{% with tag_name = 'h1' if view.is_hp else 'div' %}
		<{{ tag_name }} class="logo_bar__brand" itemprop="brand">
			<a itemprop="url" href="{{ request.route_url('home') }}index" title="Nachrichten auf ZEIT ONLINE" data-id="topnav.2.1..logo">
				<meta itemprop="name" content="ZEIT ONLINE">
				<span itemprop="logo" itemscope itemtype="http://schema.org/ImageObject">
					{{ lama.use_svg_icon('logo-zon-black', 'logo_bar__brand-logo', view.request, inline=view.inline_svg_icons) }}
					<meta itemprop="url" content="{{ request.asset_host }}/images/structured-data-publisher-logo-zon.png">
					<meta itemprop="width" content="565">
					<meta itemprop="height" content="60">
				</span>
			</a>
		</{{ tag_name }}>
		{% endwith %}
		<div class="logo_bar__menu">
			<a href="#primary_nav" title="Hauptmenü" aria-label="Hauptmenü" role="button" aria-controls="navigation" aria-expanded="false">
				{{ lama.use_svg_icon('menu', 'logo_bar__menu-icon logo_bar__menu-icon--burger', view.request, inline=view.inline_svg_icons) }}
				{{ lama.use_svg_icon('close', 'logo_bar__menu-icon logo_bar__menu-icon--close', view.request, inline=view.inline_svg_icons) }}
			</a>
		</div>
	</div>

	<!-- special teaser -->
	{% block special_teaser %}
		{% if view.is_advertorial %}
		<div class="main_nav__ad-label advertorial__ad-label">{{ view.cap_title | default('Anzeige') }}</div>
		{% else %}
		<div class="main_nav__teaser">{# planned special teaser #}</div>
		{% endif %}
	{% endblock special_teaser %}

	<!-- wrap start -->
	{% block login %}
		<div class="main_nav__community" data-dropdown="true">
			{% set esi_source = '{}login-state?for=site&context-uri={}'.format(request.route_url('home'), request.url) %}
			{{ lama.insert_esi(esi_source, 'Anmeldung nicht möglich') }}
		</div>
	{% endblock login %}
	{% if view.nav_show_ressorts %}
	<div class="main_nav__ressorts" data-dropdown="true">
		<nav role="navigation" id="primary_nav">
		{%- set navigation = view.navigation -%}
		{%- set nav_class = 'primary-nav' -%}
		{%- include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" -%}
		</nav>
	</div>
	{% endif %}
	<div class="main_nav__services" data-dropdown="true">
		{%- set navigation = view.navigation_services -%}
		{%- set nav_class = 'primary-nav-services' -%}
		{%- include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" -%}
	</div>
	<div class="main_nav__classifieds" data-dropdown="true">
		{%- set navigation = view.navigation_classifieds -%}
		{%- set nav_class = 'main-nav-classifieds' -%}
		{%- include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" -%}
	</div>
	{% if view.nav_show_search %}
	<div class="main_nav__search" data-dropdown="true">{% include "zeit.web.site:templates/inc/navigation/navigation-search.tpl" %}</div>
	{% endif %}
	<!-- wrap end -->
</div>
