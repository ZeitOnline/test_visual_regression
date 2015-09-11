{% import 'zeit.web.site:templates/macros/layout_macro.tpl' as lama %}

{% if view.comments_allowed or view.comments %}
<section class="comment-section" id="comments">
	<h3 class="visually-hidden">Kommentare</h3>
	<div class="comment-section__head comment-section__item">
	{% if view.comments %}
		<span class="comment-section__headline">
			{{ view.comments.headline }}
			{% if view.comments.pages.title %}
			<small>{{ view.comments.pages.title }}</small>
			{% endif %}
		</span>
		{% if view.comments_allowed %}
		<a href="#comment-form js-scroll" class="comment-section__button button">
			Kommentieren
		</a>
		{% endif %}
	{% else %}
		<span class="comment-section__headline">
			<span class="nowrap">Noch keine Kommentare.</span>
			<span class="nowrap">Diskutieren Sie mit.</span>
		</span>
	{% endif %}
	</div>

	{% if view.comments %}
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

		{# Show ads before the 4th comment, or before the last comment if there are less than 4 [ZON-1919] #}
		{% for comment in view.comments.comments %}

			{% if (loop.length < 4 and loop.last ) or loop.index == 4 -%}
				{% if view.context.advertising_enabled -%}
				<div class="comment__ad">
					{{ lama.adplace(view.banner(8), view) }}
				</div>
				{%- endif %}
			{% endif %}

		<article id="cid-{{ comment.cid }}" class="comment
			{%- if not view.comments.sort in ('promoted', 'recommended') %}
				{%- if comment.is_reply %} comment--indented{% else %} js-comment-toplevel{% endif %}
			{%- endif %}
			{%- if comment.is_author %} comment--author{% endif %}
			{%- if comment.is_promoted %} comment--promoted{% endif %}
			{%- if comment.recommendations %} comment--recommended{% endif %}
			{%- if comment.img_url %} comment--avatar{% endif %}">
			<div class="comment__container">
				<div class="comment-meta">
					{% if comment.img_url %}
					<div class="comment-meta__avatar">
						<img alt="Avatarbild von {{ comment.name }}" src="{{ comment.img_url }}">
					</div>
					{% endif %}
					<div class="comment-meta__name">
						{% if comment.is_author %}
						<span title="{{ comment.role }}" class="comment-meta__badge comment-meta__badge--author">
							{{ lama.use_svg_icon('promoted', 'comment-meta__icon comment-meta__icon--author', request) }}
						</span>
						{% endif %}
						<a href="{{ comment.userprofile_url }}">{{ comment.name }}</a>
					</div>
					<a  class="comment-meta__date" href="{{ '{0}?cid={1}#cid-{1}'.format(view.content_url, comment.cid) }}">
						#{{ comment.shown_num }} &nbsp;—&nbsp; {{ comment.created | format_comment_date }}
					</a>

					<div class="comment-meta__badge comment-meta__badge--recommended" title="Leserempfehlungen"{% if not comment.recommendations %} style="display:none"{% endif %}>
						{{ lama.use_svg_icon('recommended', 'comment-meta__icon comment-meta__icon--recommended', request) }}
						<span class="js-comment-recommendations">{{ comment.recommendations }}</span>
					</div>

					{% if comment.is_promoted %}
						<div class="comment-meta__badge comment-meta__badge--promoted">
							{{ lama.use_svg_icon('promoted', 'comment-meta__icon comment-meta__icon--promoted', request) }}
							Redaktionsempfehlung
						</div>
					{% endif %}
				</div>
				<div class="comment__body">
					{{ comment.text | safe }}
				</div>
				<div class="comment__reactions">
					{% if view.comments_allowed -%}
					<a class="comment__reaction js-reply-to-comment" data-cid="{{ comment.cid }}" href="{{ view.request | append_get_params(action='comment', pid=comment.cid) }}#comment-form" title="Antworten">
						{{ lama.use_svg_icon('comment-reply', 'comment__icon comment__icon-reply', request) }}
						<span class="comment__action">Antworten</span>
					</a>
					{% endif -%}
					<a class="comment__reaction js-report-comment" data-cid="{{ comment.cid }}" href="{{ view.request | append_get_params(action='report', pid=comment.cid) }}#report-comment-form" title="Melden">
						{{ lama.use_svg_icon('comment-report', 'comment__icon comment__icon-report', request) }}
						<span class="comment__action">Melden</span>
					</a>
					<a class="comment__reaction js-recommend-comment" data-cid="{{ comment.cid }}" data-fans="{{ comment.fans }}" href="{{ view.request | append_get_params(action='recommend', pid=comment.cid) }}#cid-{{ comment.cid }}" title="Empfehlen">
						{{ lama.use_svg_icon('comment-recommend', 'comment__icon comment__icon-recommend', request) }}
						<span class="comment__action">Empfehlen</span>
					</a>
				</div>
			</div>
		</article>
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
		<esi:include src="{{ view.content_url }}/report-form?pid={{ view.request.GET.pid }}" onerror="continue" />
	{% else %}
		{% if view.request.GET.error %}
		    <esi:include src="{{ view.content_url }}/comment-form?error={{ view.request.GET.error }}" onerror="continue" />
		{% else %}
		    <esi:include src="{{ view.content_url }}/comment-form?pid={{ view.request.GET.pid }}" onerror="continue" />
		{% endif %}
	{% endif %}

	<script type="text/template" id="js-report-success-template">
		<div class="comment-form__response--success">
			Danke! Ihre Meldung wird an die Redaktion weitergeleitet.
		</div>
	</script>

</section>
{% endif %}
