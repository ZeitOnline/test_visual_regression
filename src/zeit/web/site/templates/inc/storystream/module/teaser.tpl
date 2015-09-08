{% set atom = module | first_child %}
{% set blockname = 'storystream-teaser' %}
<article class="{{ blockname }}">
	<div class="{{ blockname }}__header">
		<span class="{{ blockname }}__date{% if atom.tldr_milestone == True %} {{ blockname }}__date--milestone{% endif %}">
			{{ atom.tldr_date | format_date(None, 'dd.MM.yy') }}
		</span>
		<h2 class="{{ blockname }}__title">{{ atom.tldr_title | hide_none }}</h2>
	</div>
	<div class="{{ blockname }}__content">
		<p class="{{ blockname }}__text">
			{{ atom.tldr_text }}
			<a class="{{ blockname }}__link" href="{{ atom.uniqueId | create_url }}">mehr lesen</a>
		</p>

		{% set image = get_image(module) %}
		{% if image %}
			{% set href = atom.uniqueId | create_url %}
			{% set module_layout = blockname %}
			{% include "zeit.web.site:templates/inc/linked-image.tpl" %}
		{% endif %}
	</div>
</article>
