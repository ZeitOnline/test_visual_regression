{% set blockname = 'storystream-markup' %}
{% if module_loop.first %}
	{% set blockname_modifier = 'first' %}
{% elif module_loop.last %}
	{% set blockname_modifier = 'last' %}
{% endif %}
<div class="{{ blockname | with_mods(blockname_modifier) }}">
	<div class="{{ '{}__container'.format(blockname) | with_mods(blockname_modifier) }}">
		<div class="{{ '{}__content'.format(blockname) | with_mods(blockname_modifier) }}">
		    <h2 class="{{ blockname }}__title">{{ module.title | hide_none }}</h2>
		    <div class="{{ '{}__text'.format(blockname) | with_mods(blockname_modifier) }}">
		        {{ module.text | hide_none | safe }}
		    </div>
		</div>
	</div>
</div>
