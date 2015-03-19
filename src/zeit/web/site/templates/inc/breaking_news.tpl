{%- set breaking_news = view.breaking_news -%}

{% if breaking_news.published or debug_breaking_news() -%}
<div class="breaking-news-banner">
    <a class="breaking-news-banner__link" onclick="ZEIT.clickGA(['_trackEvent', 'breakingnews', 'click', '{{ breaking_news.doc_path }}']);" id="hp.banner.breakingnews.title.{{ breaking_news.doc_path }}" href="{{ breaking_news.uniqueId | translate_url }}">Eilmeldung <span class="breaking-news-banner__time">{{ breaking_news.date_string }}</span> <span class="breaking-news-banner__title">{{ breaking_news.title }}</span></a>
</div>
{%- endif %}
