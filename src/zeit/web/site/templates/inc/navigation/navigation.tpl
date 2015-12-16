{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
<div class="main_nav">
	<!-- logo -->
	<div itemscope itemtype="http://schema.org/Organization" class="logo_bar">
		{% with tag_name = 'h1' if view.is_hp else 'div' %}
		<{{ tag_name }} class="logo_bar__brand" itemprop="brand">
			<a itemprop="url" role="img" href="{{ request.route_url('home') }}index" title="Nachrichten auf ZEIT ONLINE" data-id="topnav.2.1..logo">
				{# Metatag to show Google the image, see http://stackoverflow.com/questions/18130827/schema-org-give-a-div-a-itemprop-image -#}
				<meta itemprop="logo" content="{{ request.asset_host }}/icons/site/zon-logo-desktop.png">
				<meta itemprop="name" content="ZEIT ONLINE">
				<object class="logo_bar__brand-logo" data="{{ view.request.asset_host }}/images/logo-zon-black.svg" type="image/svg+xml">
					<img src="{{ view.request.asset_host }}/images/logo-zon-black.png" alt="ZEIT ONLINE" />
				</object>
			</a>
		</{{ tag_name }}>
		{% endwith %}
		<div class="logo_bar__menu">
			<a href="#primary_nav" title="Hauptmenü" aria-label="Hauptmenü" role="button" aria-controls="navigation" aria-expanded="false">
				{{ lama.use_svg_icon('menu', 'logo_bar__menu-icon logo_bar__menu-icon--burger', view.request) }}
				{{ lama.use_svg_icon('close', 'logo_bar__menu-icon logo_bar__menu-icon--close', view.request) }}
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
	<div class="main_nav__community" data-dropdown="true">
		{% set esi_source = '{}/login-state?context-uri={}'.format(request.route_url('home'), request.url) %}
		{{ lama.insert_esi(esi_source, 'Anmeldung nicht möglich', view.is_dev_environment) }}
	</div>
	<div class="main_nav__ressorts" data-dropdown="true">
		<nav role="navigation" id="primary_nav">
		{%- set navigation = view.navigation -%}
		{%- set nav_class = 'primary-nav' -%}
		{%- include "zeit.web.site:templates/inc/navigation/navigation-list.tpl" -%}
		</nav>
	</div>
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
	<div class="main_nav__search" data-dropdown="true">{% include "zeit.web.site:templates/inc/navigation/navigation-search.tpl" %}</div>
	<!-- wrap end -->
</div>
