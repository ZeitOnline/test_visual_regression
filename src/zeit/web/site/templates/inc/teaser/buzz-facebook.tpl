{%- extends "zeit.web.site:templates/inc/teaser/default.tpl" -%}

{% block layout %}teaser-buzz{% endblock %}
{% block meetrics %}{% endblock %}
{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_container %}
	<span class="{{ self.layout() }}__metadata">
		{{ lama.use_svg_icon('buzz-shared', self.layout() + '__icon', request) }}
		{{ teaser.score | pluralize('Nie geteilt', '{} mal geteilt') }}
	</span>
{% endblock %}
