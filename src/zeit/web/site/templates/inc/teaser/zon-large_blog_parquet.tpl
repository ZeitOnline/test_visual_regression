{%- extends "zeit.web.site:templates/inc/teaser/zon-large_parquet.tpl" -%}

{% block teaser_journalistic_format %}
	<div class="blog-format blog-format--large">
		<span class="blog-format__marker blog-format__marker--large">Blog</span>
		<span class="blog-format__name blog-format__name--large">
			{{ teaser.blog.name | hide_none }}
		</span>
	</div>
{% endblock %}

{% block teaser_kicker %}
	<span class="{{ self.layout() }}__kicker {{ self.layout() }}__kicker--blog">{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</span>
{% endblock %}
