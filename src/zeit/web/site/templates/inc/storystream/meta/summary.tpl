<div class="storystream-summary">
	<div class="storystream-summary__container">
	    <p itemprop="description">{{ view.context.subtitle }}</p>
	    <p>
	        {% set byline = view.context | get_byline('main') %}
	        {% include 'zeit.web.core:templates/inc/meta/byline.html' %}
	    </p>
	</div>
</div>
