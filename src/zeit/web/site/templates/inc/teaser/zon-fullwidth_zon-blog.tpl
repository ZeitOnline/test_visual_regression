{%- extends "zeit.web.site:templates/inc/teaser/zon-fullwidth.tpl" -%}

{% block layout %}teaser-fullwidth-blog{% endblock %}

{% block teaser_format_marker %}
	<span class="{{ self.layout() }}__marker">Blog</span>
{% endblock %}

{% block teaser_format_name %}
	<span class="{{ self.layout() }}__name">
		{{ teaser.blog.name | hide_none }}
		{% if teaser.teaserSupertitle or teaser.supertitle %} / {% endif %}
	</span>
{% endblock %}
