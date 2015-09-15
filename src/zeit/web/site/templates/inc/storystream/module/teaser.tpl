{% set atom = module | first_child %}
{% set blockname = 'storystream-teaser' %}
<{{ teaser_tag or 'div' }} class="{{ blockname }}">
	<div class="{{ blockname }}__container">
		<div class="{{ blockname }}__content">
			<div class="{{ blockname }}__header">
				<span class="{{ 'storystream-teaser__date' | with_mods(teaser_modifier) }}">
					{{ atom.tldr_date | format_date(None, 'dd.MM.yy') }}
				</span>
				{% block teaser_title -%}
					<h2 class="{{ blockname }}__title">{{ atom.tldr_title or atom.teaserTitle or atom.title | hide_none }}</h2>
				{%- endblock teaser_title %}
			</div>
			<div class="{{ blockname }}__text">
				<p class="{{ 'storystream-teaser__description' | with_mods(teaser_modifier) }}">
					{{ atom.tldr_text or atom.teaserText }}&nbsp;<a class="{{ blockname }}__link" href="{{ atom.uniqueId | create_url }}">mehr lesen</a>
				</p>
				<pre style="background:#c0ff33;">DEBUGtpuppe: {{ atom | obj_debug }}</pre>
				{% set image = get_image(module) %}
				{% if image %}
					{% set href = atom.uniqueId | create_url %}
					{% set module_layout = blockname %}
					{% include "zeit.web.site:templates/inc/linked-image.tpl" %}
				{% endif %}
			</div>
		</div>
	</div>
</{{ teaser_tag or 'div' }}>
