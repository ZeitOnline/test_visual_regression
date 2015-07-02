{%- extends "zeit.web.site:templates/inc/teaser/zon-fullwidth.tpl" -%}



{% block teaser_journalistic_format %}
	<div class="blog-format blog-format--fullwidth">
		<span class="blog-format__marker blog-format__marker--fullwidth">Blog</span>
		<span class="blog-format__name blog-format__name--fullwidth">
			{{ teaser.blog.name | hide_none }}
		</span>
	</div>
{% endblock %}

{% block teaser_kicker %}
	<span class="{{ self.layout() }}__kicker {{ self.layout() }}__kicker--blog">{{ teaser.teaserSupertitle or teaser.supertitle | hide_none }}</span>
{% endblock %}
