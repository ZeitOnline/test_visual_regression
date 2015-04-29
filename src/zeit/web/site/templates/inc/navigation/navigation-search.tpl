<form accept-charset="utf-8" method="get" class="search" role="search" action="{{ view.request.route_url('home') }}suche/index">
	<label for="q" class="hideme">suchen</label>
	{# Please don't break line here, due to inline-block state. #}
	<input class="search__input" id="q" name="q" type="search" placeholder="Suche" tabindex="1"><button class="search__button" type="submit" tabindex="2">
		<a>
			<span class="icon-zon-logo-navigation_suche search__button__image main_nav__icon--plain"></span>
			<span class="icon-zon-logo-navigation_suche-hover search__button__image main_nav__icon--hover"></span>
		</a>
	</button>
</form>
