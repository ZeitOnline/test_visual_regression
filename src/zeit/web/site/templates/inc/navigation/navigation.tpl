<div class="main_nav">
	<!-- logo -->
	<div itemscope itemtype="http://schema.org/Organization" class="logo_bar">
		{% with tag_name = 'h1' if view.is_hp else 'div' %}
		<{{ tag_name }} class="logo_bar__image" itemprop="brand">
			<a itemprop="url" role="img" href="http://{{ view.request.host }}/index" title="Nachrichten auf ZEIT ONLINE" class="icon-zon-logo-desktop" id="hp.global.topnav.centerpages.logo">
				{# Metatag to show Google the image, see http://stackoverflow.com/questions/18130827/schema-org-give-a-div-a-itemprop-image -#}
				<meta itemprop="logo" content="http://{{ view.request.host }}/static/icons/zon-logo-desktop.png">
				ZEIT ONLINE
			</a>
		</{{ tag_name }}>
		{% endwith %}
		<div class="logo_bar__menue">
			<a href="#primary_nav" title="Hauptmenü" aria-label="Hauptmenü" role="button" aria-controls="navigation" aria-expanded="false">
				<div class="logo_bar__menue__image main_nav__icon--plain icon-zon-logo-navigation_menu"></div>
				<div class="logo_bar__menue__image main_nav__icon--hover icon-zon-logo-navigation_menu-hover"></div>
			</a>
		</div>
	</div>
	<!-- special teaser -->
	<div class="main_nav__teaser">{# planned special teaser #}</div>

	<!-- wrap start -->
	<div class="main_nav__community" data-dropdown="true">
                <esi:include src="http://{{ view.request.host }}/login-state" />
		<a href="http://{{ view.request.host }}/beta/index" class="beta-badge beta-badge--navigation">Beta</a>
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
	<div class="beta-notice" data-dropdown="true">
		<div>Sie benutzen die neue ZEIT ONLINE Beta.</div>
		<div><a class="beta-notice__link" href="http://www.zeit.de/beta">Zurück zur klassischen Version?</a></div>
	</div>
	<!-- wrap end -->
</div>
