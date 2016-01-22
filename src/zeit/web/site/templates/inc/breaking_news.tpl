{% if view.breaking_news.published or debug_breaking_news(request) %}
	<div class="breaking-news-banner">
		<a class="breaking-news-banner__link" href="{{ view.breaking_news.uniqueId | create_url }}" data-id="topnav....breakingnews">
			<strong class="breaking-news-banner__label">Eilmeldung</strong> <span class="breaking-news-banner__time">{{ view.breaking_news.date_first_released | format_date('time_only') }}</span>
			<span class="breaking-news-banner__title">{{ view.breaking_news.title }}</span>
		</a>
	</div>
{% endif %}
