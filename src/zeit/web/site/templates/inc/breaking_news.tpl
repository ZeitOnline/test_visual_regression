{%- set breaking_news = view.breaking_news -%}

<div class="breaking-news-banner">
    <a class="breaking-news-banner__link" onclick="ZEIT.clickGA(['_trackEvent', 'breakingnews', 'click', '/wirtschaft/2015-03/atomausstieg-kernkraftwerk-atomenergie']);" id="hp.banner.breakingnews.title./wirtschaft/2015-03/atomausstieg-kernkraftwerk-atomenergie" href="{{ breaking_news.uniqueId | translate_url }}">Eilmeldung <span class="breaking-news-banner__time">{{ breaking_news.date_string }}</span> <span class="breaking-news-banner__title">{{ breaking_news.title }}</span></a>
</div>
