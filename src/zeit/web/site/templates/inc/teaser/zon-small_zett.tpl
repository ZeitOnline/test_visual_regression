{% extends "zeit.web.site:templates/inc/teaser/zon-small.tpl" %}

{% block teaser_kicker %}
	<span class="{{ '%s__kicker' | format(self.layout()) | with_mods('zett-parquet') }}">
	    {{- teaser.teaserSupertitle or teaser.supertitle -}}
	</span>
	{%- if teaser.teaserSupertitle or teaser.supertitle -%}
		<span class="visually-hidden">:</span>
	{% endif %}
{% endblock %}


{% block teaser_label %}
	{% if module[0].is_ad %}
		<span class="{{ self.layout() }}__label">Anzeige</span>
	{% endif %}
{% endblock %}
