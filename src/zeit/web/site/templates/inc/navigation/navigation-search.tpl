{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}
<form accept-charset="utf-8" method="get" class="search" role="search" action="{{ view.request.route_url('home') }}suche/index">
	<label for="q" class="visually-hidden">suchen</label>
	<input class="search__input" id="q" name="q" type="search" placeholder="Suche">
	<button class="search__button" type="submit">
		{{ lama.use_svg_icon('search', 'search__icon', view.package) }}
	</button>
</form>
