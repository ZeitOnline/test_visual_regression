{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-buzz{% endblock %}
{% block meetrics %}{% endblock %}
{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_container %}
	<span class="{{ self.layout() }}__metadata">
		{{ lama.use_svg_icon('buzz-comment', self.layout() + '__icon', request) }}
		<a class="{{ self.layout() }}__commentcount js-update-commentcount" href="{{ teaser.uniqueId | create_url }}#comments" title="Kommentare anzeigen">
			{{ teaser.score | pluralize('Keine Kommentare', '{} Kommentar', '{} Kommentare') }}
		</a>
	</span>
{% endblock %}
