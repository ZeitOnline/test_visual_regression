{% import "zeit.web.campus:templates/macros/layout_macro.tpl" as lama %}
<div class="header__brand">
	<div class="header__publisher" id="publisher" itemprop="publisher" itemscope itemtype="http://schema.org/Organization">
		<a itemprop="url" href="{{ request.route_url('home') }}campus/index">
			<meta itemprop="name" content="ZEIT CAMPUS Online">
			<span itemprop="logo" itemscope itemtype="http://schema.org/ImageObject">
				{{ lama.use_svg_icon('logo-zco', 'header__logo', view.request) }}
				{# The "logo" dimensions must not exceed 600x60 -#}
				<meta itemprop="url" content="{{ request.asset_host }}/images/structured-data-publisher-logo-zco.png">
				<meta itemprop="width" content="347">
				<meta itemprop="height" content="60">
			</span>
		</a>
	</div>
	<div class="header__menu-link">
		{{ lama.use_svg_icon('menu', 'header__menu-icon', view.request) }}
		<span class="visually-hidden">Menu öffnen</span>
	</div>
</div>

<div class="nav">
	<div class="nav__home">
		<h2 class="nav__home-title"><a href="{{ request.route_url('home') }}index">ZEIT ONLINE</a></h2>
	</div>
	<nav class="nav__services">
		<h2 class="nav__services-title" tabindex="0"><span class="nav__dropdown">Service</span></h2>
		<ul class="nav__services-list">
			<li><a href="#">ZEIT Wissen</a></li>
			<li><a href="#">ZEIT Geschichte</a></li>
			<li><a href="#">Immobilien</a></li>
			<li><a href="#">Partnersuche</a></li>
			<li><a href="#">Automarkt</a></li>
			<li><a href="#">Jobs</a></li>
			<li><a href="#">Apps</a></li>
		</ul>
	</nav>
	<div class="nav__login">
	{% if False %}
		<a href="#" class="nav__login-link">
			Anmelden
			<span class="nav__login-register">
				/ Registrieren
				{{ lama.use_svg_icon('login', 'nav__login-icon', view.request) }}
			</span>
		</a>
	{% else %}
		<h2 class="nav__login-title" tabindex="0">
			<span class="nav__user-picture"></span>
			<span class="nav__user-name">crauscher sfg as afb afbafdb adfbadf dfabdaf bdaf ad</span>
		</h2>
		<ul class="nav__login-list">
			<li><a href="#">Account</a></li>
			<li>
				<a href="#">
					Abmelden
					{{ lama.use_svg_icon('login', 'nav__login-icon', view.request) }}
				</a>
			</li>
		</ul>
	{% endif %}
	</div>
	<div class="nav__primary">
		<nav class="nav__topics">
			<h2 class="nav__topics-title"><a href="#">Themen</a></h2>
			<ul class="nav__topics-list">
				<li><a href="#">Auslandsstudium</a></li>
				<li><a href="#">Bafög</a></li>
				<li><a href="#">Studienplatzvergabe</a></li>
			</ul>
			<a class="nav__topics-link" href="#">Alle Themen</a>
		</nav>
		<nav class="nav__tools">
			<h2 class="nav__tools-title"><a href="#what"><span class="nav__dropdown">Was soll ich studieren?</span></a></h2>
			<ul class="nav__tools-list">
				<li><a href="#si">Studium-Interessentest</a></li>
				<li><a href="#">Suchmaschine für Studiengänge</a></li>
				<li><a href="#">CHE Hochschulranking</a></li>
			</ul>
		</nav>
	</div>
	<nav class="nav__more">
		<h2 class="nav__more-title" tabindex="0"><span class="nav__dropdown">Mehr</span></h2>
		<ul class="nav__more-list" id="more-list">
			<li><a href="#">Abo</a></li>
			<li><a href="#">Shop</a></li>
			<li><a href="#">ePaper</a></li>
		</ul>
	</nav>

</div>
