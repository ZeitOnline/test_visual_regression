{% set blockname = 'storystream-sharing' %}
{% set content_url = view.content_url ~ '{0}?wt_zmc=sm.ext.zonaudev.{0}.ref.zeitde.share.link.x&utm_medium=sm&utm_source={0}_zonaudev_ext&utm_campaign=ref&utm_content=zeitde_share_link_x' %}
<div class="{{ blockname }}">
	<div class="{{ blockname }}__container">
		<div class="{{ blockname }}__content">
			{#<a class="button {{ blockname }}__button" href="#">Folgen</a>#}
			<a class="{{ blockname }}__link {{ blockname }}__link--facebook" href="http://www.facebook.com/sharer/sharer.php?u={{ content_url.format('facebook') | urlencode }}" target="_blank" data-id="articlehead.1.1.social.facebook">
				{{ lama.use_svg_icon('storystream-facebook', 'storystream-sharing__icon', view.package) }}
			</a>
			<a class="{{ blockname }}__link {{ blockname }}__link--twitter" href="http://twitter.com/intent/tweet?text={{ view.title | urlencode }}&amp;via=zeitonline&amp;url={{ content_url.format('twitter') | urlencode }}" target="_blank" data-id="articlehead.1.2.social.twitter">
				{{ lama.use_svg_icon('storystream-twitter', 'storystream-sharing__icon', view.package) }}
			</a>
			<a class="{{ blockname }}__link {{ blockname }}__link--whatsapp" href="whatsapp://send?text={{ '%s - Artikel auf %s: %s' | format(view.title, view.publisher_name, content_url.format('whatsapp')) | urlencode }}" data-id="articlehead.1.3.social.whatsapp">
				{{ lama.use_svg_icon('storystream-whatsapp', 'storystream-sharing__icon', view.package) }}
			</a>
		</div>
	</div>
</div>
