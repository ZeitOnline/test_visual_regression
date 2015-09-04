{% set atom = module | first_child %}
{% set blockname = 'storystream-teaser' %}
<article class="{{ blockname }}">
	<span class="{{ blockname }}__date{% if atom.tldr_milestone == True %} {{ blockname }}__date--milestone{% endif %}">
		{{ atom.tldr_date | format_date(None, 'dd.MM.yy') }}
	</span>
	<h2 class="{{ blockname }}__heading">{{ atom.tldr_title | hide_none }}</h2>
	<p>
		{{ atom.tldr_text }}
		<a class="{{ blockname }}__link" href="{{ atom.uniqueId | create_url }}">mehr lesen</a>
	</p>
</article>
