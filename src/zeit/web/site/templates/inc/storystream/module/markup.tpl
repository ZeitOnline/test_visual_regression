{% set blockname = 'storystream-markup' %}
{% if region_loop.index <= 2 and area_loop.first and module_loop.first %}
	{% set blockname_modifier = 'first' %}
{% elif region_loop.last and area_loop.last and module_loop.last %}
	{% set blockname_modifier = 'last' %}
{% endif %}
<div class="{{ blockname | with_mods(blockname_modifier) }}">
	<div class="{{ '{}__container'.format(blockname) | with_mods(blockname_modifier) }}">
		<div class="{{ '{}__content'.format(blockname) | with_mods(blockname_modifier) }}">
		    <h2 class="{{ blockname }}__title">{{ module.title }}</h2>
		    <div class="{{ '{}__text'.format(blockname) | with_mods(blockname_modifier) }}">
		        {{ module.text | safe }}
		    </div>
		</div>
	</div>
</div>
