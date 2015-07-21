{%- extends "zeit.web.site:templates/inc/teaser/zon-large.tpl" -%}

{% block teaser_journalistic_format %}
	<div class="blog-format">
		<span class="blog-format__marker">Blog</span>
		<span class="blog-format__name">
			{{ teaser.blog.name | hide_none }}
		</span>
	</div>
{% endblock %}

{% block teaser_kicker %}
	<span class="{{ self.layout() }}__kicker {{ self.layout() }}__kicker--blog">{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</span>
{% endblock %}

