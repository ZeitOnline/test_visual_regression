{% set blockname = 'storystream-sharing' %}
<div class="{{ blockname }}">
	<div class="{{ blockname }}__container">
		<div class="{{ blockname }}__content">
			{#<a class="button {{ blockname }}__button" href="#">Folgen</a>#}
			<a class="{{ blockname }}__link {{ blockname }}__link--facebook" href="http://www.facebook.com/sharer/sharer.php?u={{ view.content_url + '?wt_zmc=sm.int.zonaudev.facebook.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=facebook_zonaudev_int&utm_campaign=facebook_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" data-id="articlehead.1.1.social.facebook">
				{{ lama.use_svg_icon('storystream-facebook', 'storystream-sharing__icon', view.package) }}
			</a>
			<a class="{{ blockname }}__link {{ blockname }}__link--twitter" href="http://twitter.com/intent/tweet?text={{ view.title | urlencode }}&amp;via=zeitonline&amp;url={{ view.content_url + '?wt_zmc=sm.int.zonaudev.twitter.ref.zeitde.dskshare.link.x&utm_medium=sm&utm_source=twitter_zonaudev_int&utm_campaign=twitter_referrer&utm_content=zeitde_dskshare_link_x' | urlencode }}" target="_blank" data-id="articlehead.1.2.social.twitter">
				{{ lama.use_svg_icon('storystream-twitter', 'storystream-sharing__icon', view.package) }}
			</a>
			<a class="{{ blockname }}__link {{ blockname }}__link--whatsapp" href="whatsapp://send?text={{ (view.title + ' - Artikel auf ZEIT ONLINE: ' + view.content_url) | urlencode }}" data-id="articlehead.1.3.social.whatsapp">
				{{ lama.use_svg_icon('storystream-whatsapp', 'storystream-sharing__icon', view.package) }}
			</a>
		</div>
	</div>
</div>
