{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}


	{#
	<pre>
	SHOW: {{ view.comment_area.show }}
	SHOW_COMMENT_FORM: {{ view.comment_area.show_comment_form }}
	SHOW_COMMENTS: {{ view.comment_area.show_comments }}
	NO_COMMENTS: {{ view.comment_area.show_comments }}
	MESSAGE: {{ view.comment_area.message }}
	NOTE: {{ view.comment_area.note }}
	USER_BLOCKED: {{ view.comment_area.user_blocked }}
	</pre>
	#}

{% if view.comment_area.show %}

{% include "zeit.web.site:templates/inc/comments/premoderation.tpl" %}
<section class="comment-section" id="comments">
	<h3 class="visually-hidden">Kommentare</h3>
	<div class="comment-section__head comment-section__item">
	{% if view.comment_area.show_comments %}
		<span class="comment-section__headline">
			{{ view.comments.headline }}
			{% if view.comments.pages.title %}
			<small>{{ view.comments.pages.title }}</small>
			{% endif %}
		</span>
		{% if view.comment_area.show_comment_form %}
		<a href="#comment-form" class="comment-section__button button js-scroll">
			Kommentieren
		</a>
		{% endif %}
	{% elif view.comment_area.no_comments %}
		<span class="comment-section__headline">
			<span class="nowrap">Noch keine Kommentare.</span>
			<span class="nowrap">Diskutieren Sie mit.</span>
		</span>
	{% else %}
		<span class="comment-section__headline">
			<span class="nowrap">Kommentare</span>
		</span>
	{% endif %}

	{% if view.comment_area.message  %}
		<div class="comment-section__message">
			{{ view.comment_area.message }}
		</div>
	{% endif %}
	</div>

	{% if view.comment_area.show_comments %}
	<div class="comment-preferences">
		<div class="comment-preferences__container">
			{# funky future feature?
			<a class="comment-preferences__item nowrap" href="{{ request.url }}#comments">
				{{ lama.use_svg_icon('spinner', 'comment-preferences__icon comment-preferences__icon--spinner', request) }}
				Auto-Aktualisierung an
			</a>
			#}
			{% if view.comments.sort == 'asc' %}
				{% set href = '{}?sort=desc'.format(view.request.path_url) %}
				{% set label = 'Neueste zuerst' %}
			{% elif view.comments.sort == 'desc' %}
				{% set href = view.request.path_url %}
				{% set label = 'Älteste zuerst' %}
			{% else %}
				{% set href = view.request.path_url %}
				{% set label = 'Alle Kommentare anzeigen' %}
			{% endif %}
			<a class="comment-preferences__item nowrap" href="{{ href }}#comments">
				{{ lama.use_svg_icon('sorting', 'comment-preferences__icon comment-preferences__icon--sorting', request) }}
				<span>{{ label }}</span>
			</a>
			{% if view.comments.has_promotion %}
				{% set href = '{}?sort=promoted'.format(view.request.path_url) %}
				<a class="{{ 'comment-preferences__item' | with_mods('buttonized', 'active' if view.comments.sort == 'promoted') }} nowrap" href="{{ href }}#comments">
					{{ lama.use_svg_icon('promoted', 'comment-preferences__icon comment-preferences__icon--promoted', request) }}
					<span class="comment-preferences__text">Nur Redaktionsempfehlungen</span>
				</a>
			{% endif %}
			{% if view.comments.has_recommendations %}
				{% set href = '{}?sort=recommended'.format(view.request.path_url) %}
				<a class="{{ 'comment-preferences__item' | with_mods('buttonized', 'active' if view.comments.sort == 'recommended') }} nowrap" href="{{ href }}#comments">
					{{ lama.use_svg_icon('recommended', 'comment-preferences__icon comment-preferences__icon--recommended', request) }}
					<span class="comment-preferences__text">Nur Leserempfehlungen</span>
				</a>
			{% endif %}
		</div>
	</div>

	<div id="js-comments-body">

		{# Show ads before the n-th comment, or before the last comment if there are less than n #}
		{% for comment in view.comments.comments %}

			{% if (loop.length < view.comments.ad_place and loop.last ) or loop.index == view.comments.ad_place -%}
				{% if view.context.advertising_enabled -%}
				<div class="comment__ad">
					{{ lama.adplace(view.banner(8), view) }}
				</div>
				{%- endif %}
			{% endif %}

			{% include "zeit.web.site:templates/inc/comments/comment.tpl" %}

			{% for comment in comment.replies %}
				{% include "zeit.web.site:templates/inc/comments/comment.tpl" %}
			{% endfor %}
		{% endfor %}
	</div>

	{% include "zeit.web.site:templates/inc/comments/pagination.tpl" %}

	{% else %}
		{% if view.context.advertising_enabled -%}
			<div class="comment__ad">
				{{ lama.adplace(view.banner(8), view) }}
			</div>
		{% endif %}
	{% endif %}

	{% if view.request.GET.action == 'report' %}
		{% set esi_source = '{}/report-form?pid={}'.format(view.content_url, view.request.GET.pid)  %}
	{% else %}
		{% if view.request.GET.error %}
		    {% set esi_source = '{}/comment-form?error={}'.format(view.content_url, view.request.GET.error) %}
		{% else %}
		    {% set esi_source = '{}/comment-form?pid={}'.format(view.content_url, view.request.GET.pid) %}
		{% endif %}
	{% endif %}
	{{ lama.insert_esi(esi_source, 'Kommentarformular konnte nicht geladen werden', view.is_dev_environment) }}
		<script type="text/template" id="js-report-success-template">
			<div class="comment-form__response--success">
				Danke! Ihre Meldung wird an die Redaktion weitergeleitet.
			</div>
		</script>
</section>
{% endif %}
