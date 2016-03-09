{%- extends "{0}:templates/inc/teaser/default.tpl".format(view.package) -%}

{% set ref_cp = area.referenced_cp %}
{% set topic_supertitle = area.supertitle or ref_cp.teaserSupertitle or ref_cp.supertitle %}
{% set readmore_url = area.read_more_url | create_url %}
{% if not readmore_url and ref_cp is not none %}
	{% set readmore_url = ref_cp.uniqueId | create_url %}
{% endif %}

{% block layout %}teaser-topic-main{% endblock %}
{% block teaser_journalistic_format %}{% endblock %}

{% block teaser_link %}
	{% if readmore_url %}
	<a class="{{ self.layout() }}__combined-link" title="{{ topic_supertitle }} - {{ area.title }}" href="{{ readmore_url }}">
		<span class="{{ self.layout() }}__kicker">{{ topic_supertitle }}</span>
		{%- if topic_supertitle %}<span class="visually-hidden">:</span>{% endif %}
		<span class="{{ self.layout() }}__title">{{ area.title }}</span>
	</a>
	 {% endif %}
{% endblock %}

{% block teaser_media_position_after_title %}
	{% if readmore_url %}
	<a href="{{ readmore_url }}" class="{{ self.layout() }}__button">
		{{ area.read_more | default('Alles zum Thema', true) }}
	</a>
	{% endif %}
{% endblock %}

{% block teaser_container %}{% endblock %}
