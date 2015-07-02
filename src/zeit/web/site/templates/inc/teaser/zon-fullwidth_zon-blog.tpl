{%- extends "zeit.web.site:templates/inc/teaser/zon-fullwidth.tpl" -%}

{% block layout %}teaser-fullwidth-blog{% endblock %}

{% block teaser_journlistic_format %}
	<div class="{{ self.layout() }}__journlistic-format">
		<span class="{{ self.layout() }}__marker">Blog</span>
		<span class="{{ self.layout() }}__name">
{% block teaser_journalistic_format %}
			{{ teaser.blog.name | hide_none }}
		</span>
	</div>
{% endblock %}
