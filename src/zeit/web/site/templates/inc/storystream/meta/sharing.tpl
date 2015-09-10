{% set blockname = 'storystream-sharing' %}
<div class="{{ blockname }}">
	<div class="{{ blockname }}__container">
		{#<a class="button {{ blockname }}__button" href="#">Folgen</a>#}
		<a class="{{ blockname }}__link {{ blockname }}__link--facebook" href="#">
			{{ lama.use_svg_icon('storystream-facebook', 'storystream-sharing__icon', request) }}
		</a>
		<a class="{{ blockname }}__link {{ blockname }}__link--twitter" href="#">
			{{ lama.use_svg_icon('storystream-twitter', 'storystream-sharing__icon', request) }}
		</a>
		<a class="{{ blockname }}__link {{ blockname }}__link--whatsapp" href="#">
			{{ lama.use_svg_icon('storystream-whatsapp', 'storystream-sharing__icon', request) }}
		</a>
	</div>
</div>
