{% import "zeit.web.site:templates/macros/article_macro.tpl" as blocks with context %}

{% if view.comments_allowed or view.comments %}
<section class="comment-section" id="comments">
	<div class="comment-section__head comment-section__item">
	{% if view.comments and view.comments.comment_count %}
		<span class="comment-section__headline">
			{{ view.comments.headline }}
			{% if view.comments.pages.title %}
			<small>{{ view.comments.pages.title }}</small>
			{% endif %}
		</span>
		{% if view.comments_allowed %}
		<a href="#comment-form" class="comment-section__button button">
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
	<div class="comment-section__preferences">
		<div class="comment-section__item">
			{# funky future feature?
			<a class="comment-section__link-autoupdate nowrap" href="{{ request.url }}#comments">
				{{ blocks.use_svg_icon('spinner', 'comment-section__icon-spinner') }}
				Auto-Aktualisierung an
			</a>
			#}
			{% if view.comments.sort == 'asc' %}
				{% set href = '{}?sort=desc'.format(view.request.path_url) %}
				{% set label = 'Älteste zuerst' %}
			{% else %}
				{% set href = view.request.path_url %}
				{% set label = 'Neueste zuerst' %}
			{% endif %}
			<a class="comment-section__link-sorting nowrap" href="{{ href }}#comments">
				{{ blocks.use_svg_icon('sorting', 'comment-section__icon-sorting') }}
				{{ label }}
			</a>
		</div>
	</div>

	<div id="js-comments-body">
	{% for comment in view.comments.comments %}
		{% if loop.length > 3 and loop.index == 3 %}
			{% if view.context.advertising_enabled -%}
			<div class="comment__ad">
				{{ blocks.adplace_desktop(view.banner(8)) }}
			</div>
			{%- endif %}
		{% endif %}
		<article class="comment{% if comment.is_reply %} comment--indented{% endif %}{% if comment.is_author %} comment--author{% endif %}" id="cid-{{ comment.cid }}">
			<div class="comment__container">
				{% if comment.img_url %}
				<img class="comment__avatar" alt="Avatarbild von {{ comment.name }}" src="{{ comment.img_url }}">
				{% endif %}
				<div class="comment__meta">
					{% if comment.is_promoted %}
					<span class="comment__badge comment__badge--promoted" title="Redaktionsempfehlung">&#9733;</span>
					{% endif %}
					{% if comment.is_author %}
					<span title="{{ comment.role }}">
						{{ blocks.use_svg_icon('comment-author', 'comment__badge comment__badge--author') }}
					</span>
					{% endif %}
					<a class="comment__name" href="{{ comment.userprofile_url }}">
						{{ comment.name }}
					</a>
					<span class="comment__recommendations" title="Leserempfehlungen">
					{%- if comment.recommendations -%}
						{{ comment.recommendations }} &#9733;
					{%- endif -%}
					</span>
					<a  class="comment__date" href="{{ '{0}?cid={1}#cid-{1}'.format(view.content_url, comment.cid) }}">
					#{{ comment.shown_num }} &nbsp;/&nbsp; {{ comment.created | format_comment_date }}
					</a>
				</div>
				<div class="comment__body">
					{{ comment.text | safe }}
				</div>
				<div class="comment__reactions">
					{% if view.comments_allowed -%}
					<a class="comment__reaction js-reply-to-comment" data-cid="{{ comment.cid }}" href="{{ view.request | append_get_params(action='comment', pid=comment.cid) }}#comment-form" title="Antworten">
						{{ blocks.use_svg_icon('comment-reply', 'comment__icon comment__icon-reply') }}
						<span class="comment__action">Antworten</span>
					</a>
					{% endif -%}
					<a class="comment__reaction js-report-comment" data-cid="{{ comment.cid }}" href="{{ view.request | append_get_params(action='report', pid=comment.cid) }}#report-comment-form" title="Melden">
						{{ blocks.use_svg_icon('comment-report', 'comment__icon comment__icon-report') }}
						<span class="comment__action">Melden</span>
					</a>
					<a class="comment__reaction js-recommend-comment" data-cid="{{ comment.cid }}" data-fans="{{ comment.fans }}" href="{{ view.request | append_get_params(action='recommend', pid=comment.cid) }}#cid-{{ comment.cid }}" title="Empfehlen">
						{{ blocks.use_svg_icon('comment-recommend', 'comment__icon comment__icon-recommend') }}
						<span class="comment__action">Empfehlen</span>
					</a>
				</div>
			</div>
		</article>
		{% endfor %}
	</div>

	{% include "zeit.web.site:templates/inc/comments/pagination.tpl" %}

	{% endif %}

	{% if view.request.GET.action == 'report' %}
		<esi:include src="{{ view.content_url }}/report-form?pid={{ view.request.GET.pid }}" />
	{% else %}
		<esi:include src="{{ view.content_url }}/comment-form?pid={{ view.request.GET.pid }}" />
	{% endif %}

	<script type="text/template" id="js-report-success-template">
		<div class="comment-form__response--success">
			Danke! Ihre Meldung wird an die Redaktion weitergeleitet.
		</div>
	</script>

</section>
{% endif %}
