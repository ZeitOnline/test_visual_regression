{% set blockname = 'storystream-markup' %}
<div class="{{ blockname }}">
	<div class="{{ blockname }}__content">
	    <h2 class="{{ blockname }}__title">{{ module.title | hide_none }}</h2>
	    <div class="{{ blockname }}__text">
	        {{ module.text | hide_none | safe }}
	    </div>
	</div>
</div>
