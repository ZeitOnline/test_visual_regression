<div class="main_nav">
	<!-- logo -->
	<div class="logo_bar">
		<div class="logo_bar__image">
			<a href="//{{ view.request.host }}/index" title="Nachrichten auf ZEIT ONLINE" class="icon-zon-logo-desktop" id="hp.global.topnav.centerpages.logo">
				<!--start: title-->Nachrichten auf ZEIT ONLINE<!--end: title-->
			</a>
		</div>
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
		<a href="//community.zeit.de/user/login?destination=http://{{ view.request.host }}/index" rel="nofollow" class="user" id="drupal_login">
			<span class="main_nav__community__image icon-zon-logo-navigation_login"></span>
			Anmelden
		</a>
	</div>
	<div class="main_nav__ressorts" data-dropdown="true">{% include "zeit.web.site:templates/inc/navigation/navigation-ressorts.tpl" %}</div>
	<div class="main_nav__services" data-dropdown="true">{% include "zeit.web.site:templates/inc/navigation/navigation-services.tpl" %}</div>
	<div class="main_nav__classifieds" data-dropdown="true">{% include "zeit.web.site:templates/inc/navigation/navigation-classifieds.tpl" %}</div>
	<div class="main_nav__search" data-dropdown="true">{% include "zeit.web.site:templates/inc/navigation/navigation-search.tpl" %}</div>
	<!-- wrap end -->
	{% if view.is_hp %}
	{# please don't break line here, due to inline-block state #}
	<div class="main_nav__tags">{% include "zeit.web.site:templates/inc/navigation/navigation-tags.tpl"
	%}</div><div class="main_nav__date">{{ view.displayed_last_published_semantic | format_date('long') }}</div>
	{% endif %}
</div>
