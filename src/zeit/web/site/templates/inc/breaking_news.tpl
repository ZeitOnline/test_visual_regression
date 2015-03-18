{%- set breaking_news = view.breaking_news -%}

<div class="newsflash clear">
	<div class="inner clear">
		<div class="flash">Eilmeldung</div>
		<div class="msg">
			<p><a onclick="ZEIT.clickGA(['_trackEvent', 'breakingnews', 'click', '/wirtschaft/2015-03/atomausstieg-kernkraftwerk-atomenergie']);" id="hp.banner.breakingnews.title./wirtschaft/2015-03/atomausstieg-kernkraftwerk-atomenergie" href="{{ breaking_news.uniqueId | translate_url }}">{{ breaking_news.title }}</a> | {{ breaking_news.date_string }}</p>
		</div>
	</div>
</div>
