<div class="storystream-summary">
	<div class="storystream-summary__container">
	    <p itemprop="description">{{ view.context.subtitle }}</p>
	    <p>
	        {% set byline = view.context | get_byline('main') %}
	        {% include 'zeit.web.site:templates/inc/meta/byline.tpl' %}
	    </p>
	</div>
</div>
