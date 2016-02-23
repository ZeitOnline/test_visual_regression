<article class="{% block layout %}{{ layout | default('default') }}{% endblock %} {% block teaser_modifier %}{% endblock %}{% if module.visible_mobile == False %} mobile-hidden{% endif %}"
	data-unique-id="{{ teaser.uniqueId }}"
	{% block meetrics %} data-meetrics="{{ area.kind }}"{% endblock %}
	data-clicktracking="{{ area.kind }}"
	{% block teaser_attributes %}{% endblock %}>

	{% set module_layout = 'teaser' %}
	{% include "zeit.web.core:templates/inc/asset/image_teaser.tpl" ignore missing %}

	{% block teaser_heading %}
		<h2 class="{{ self.layout() }}__heading {% block teaser_heading_modifier %}{% endblock %}">
			{% block teaser_link %}
			<a class="{{ self.layout() }}__combined-link"
			   title="{{ teaser.teaserSupertitle or teaser.supertitle }} - {{ teaser.teaserTitle or teaser.title }}"
			   href="{{ teaser | create_url | append_campaign_params }}">
				{% block teaser_kicker %}
					<span class="{{ self.layout() }}__kicker">
						{{ teaser.teaserSupertitle or teaser.supertitle -}}
					</span>
					{%- if teaser.teaserSupertitle or teaser.supertitle -%}
						<span class="visually-hidden">:</span>
					{% endif %}
				{% endblock %}
				{% block teaser_title %}
					<span class="{{ self.layout() }}__title">{{ teaser.teaserTitle or teaser.title }}</span>
				{% endblock %}
				{% block teaser_product %}
				   {# Use this for short teaser #}
				{% endblock %}
			</a>
			{% endblock teaser_link %}
		</h2>
	{% endblock teaser_heading %}
	{% block teaser_text %}
	    <p class="{{ self.layout() }}__text">{{ teaser.teaserText }}</p>
	{% endblock %}
</article>
