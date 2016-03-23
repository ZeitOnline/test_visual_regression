{% set atom = module | first_child %}
{% set blockname = 'storystream-atom' %}
<{{ atom_tag or 'div' }} class="{{ blockname }}">
	<div class="{{ blockname }}__container">
		<div class="{{ blockname }}__content">
			<div class="{{ blockname }}__header">
				<span class="{{ '{}__date'.format(blockname) | with_mods(atom_modifier) }}">
					{{ atom.tldr_date | format_date(None, 'dd.MM.yy') }}
				</span>
				{% block atom_title -%}
					<h2 class="{{ blockname }}__title">{{ atom.tldr_title or atom.teaserTitle or atom.title }}</h2>
				{%- endblock atom_title %}
			</div>
			<div class="{{ blockname }}__text">
				<p class="{{ '{}__description'.format(blockname) | with_mods(atom_modifier) }}">
					{{ atom.tldr_text or atom.teaserText }}&nbsp;<a class="{{ blockname }}__link" href="{{ atom.uniqueId | create_url }}">mehr lesen</a>
				</p>
				{% set image = get_image(module) %}
				{% if image %}
					{% set href = atom.uniqueId | create_url %}
					{% set module_layout = blockname %}
					{% include "zeit.web.core:templates/inc/asset/image_linked.tpl" %}
				{% endif %}
			</div>
		</div>
	</div>
</{{ atom_tag or 'div' }}>
