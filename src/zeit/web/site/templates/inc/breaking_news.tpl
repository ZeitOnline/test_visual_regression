{%- set breaking_news = view.breaking_news -%}

{% if breaking_news.published or debug_breaking_news(request) -%}
    <a class="breaking-news-banner" href="{{ breaking_news.uniqueId | create_url }}">
        <strong class="breaking-news-banner__label">Eilmeldung</strong> <span class="breaking-news-banner__time">{{ view.breaking_news.date_first_released | format_date('time_only') }}</span>
        <span class="breaking-news-banner__title">{{ breaking_news.title }}</span>
    </a>
{%- endif %}
