{% extends "zeit.web.site:templates/inc/area/default.html" %}

{% if area is undefined %}
{% set area = view %}
{% endif %}

{% set module_layout = 'teaser-gallery' %}

{% block before_module_list %}
	{{ cp.section_heading('Fotostrecken', 'Alle Fotostrecken', 'foto/index', view) }}
{% endblock %}

{% block module_list %}
	<div class="{{ module_layout }}-group__container">
		{{ super() }}
	</div>
{% endblock %}

{% block after_module_list %}
	<a href="{{ view.request.route_url('home') }}foto/index"
		class="button {{ module_layout }}-group__button js-gallery-teaser-shuffle"
		{# The random segment in the url below is supposed to generate ten (somewhat)
		different versions of this area that will still be varnish-cacheable.
		The actual value will be set via JS just before the request. #}
		data-sourceurl="{{ view.content_url }}/area/___JS-RANDOM___/{{ area.uniqueId.rsplit('/', 1)[-1] }}">
		{{ lama.use_svg_icon('shuffle', '{}-group__shuffle-icon'.format(module_layout), request) }}Andere laden
	</a>
{% endblock %}
