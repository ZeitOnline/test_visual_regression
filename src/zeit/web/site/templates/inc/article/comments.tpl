<section class="comment-section" id="comments">
	<div class="comment-section__head">
		{% if view.comments and view.comments.comment_count %}
			<span class="comment-section__headline">
				{%- if view.comments.comment_count != 1 -%}
					{{ view.comments.comment_count }} Kommentare
				{%- else -%}
					1 Kommentar
				{%- endif -%}
			</span>
			<a href="#comment-form" class="comment-section__cta">
				Kommentieren
			</a>
		{% else %}
			<span class="comment-section__headline">
				<span class="nowrap">Noch keine Kommentare.</span>
				<span class="nowrap">Diskutieren Sie mit.</span>
			</span>
		{% endif %}
	</div>

{% if view.comments %}
	{% for comment in view.comments.comments[:20] %}
	<article class="comment{% if comment.is_reply %} comment--indented{% endif %}{% if comment.is_author %} comment--author{% endif %}" id="cid-{{ comment.cid }}">
		<div class="comment__container">
			{% if comment.img_url %}
			<img class="comment__avatar" alt="Avatarbild von {{ comment.name | e }}" src="{{ comment.img_url }}">
			{% endif %}
			<div class="comment__meta">
				{% if comment.is_author %}
				<span class="icon-comment-zon-author-badge"></span>
				{% endif %}
				<a class="comment__name" href="{{ comment.userprofile_url }}">
					{{ comment.name | e }}
				</a>
				{% if comment.recommendations %}
				{# Special-Char: &#9733; = Black Star #}
				<span class="comment__recommendations" title="{{ comment.recommendations }} Leserempfehlung{% if comment.recommendations != 1 %}en{% endif %}">
					{{ comment.recommendations }} &#9733;
				</span>
				{% endif %}
				<a  class="comment__date" href="#cid-{{ comment.cid }}">
				#{{ loop.index }} &nbsp;/&nbsp; {{ comment.timestamp | format_date_ago() }}
				</a>
			</div>
			<div class="comment__body">
				{{ comment.text | safe }}
			</div>
			<div class="comment__reactions">
				<a class="comment__reaction" href="#cid-{{ comment.cid }}" title="Antworten">
					<span class="icon-comment-reactions-reply"></span>
					<span class="comment__action">Antworten</span>
				</a>
				<a class="comment__reaction" href="#cid-{{ comment.cid }}" title="Melden">
					<span class="icon-comment-reactions-report"></span>
					<span class="comment__action">Melden</span>
				</a>
				<a class="comment__reaction" href="#cid-{{ comment.cid }}" title="Empfehlen">
					<span class="icon-comment-reactions-recommend"></span>
					<span class="comment__action">Empfehlen</span>
				</a>
			</div>
		</div>
	</article>
	{% endfor %}
{% endif %}

{% if view.request.authenticated_userid -%}
	<form class="comment-form" action="{{ view.comments.comment_post_url }}" method="POST" id="comment-form">
		<div class="">
	        {% if view.request.session.user.picture %}
			<img class="comment-form__avatar" alt="Avatarbild von {{ view.request.session.user.name | e }}" src="{{ view.request.session.user.picture }}">
			{% endif %}
			Angemeldet als
			<a class="comment-form__username" href="{{ view.request.registry.settings.community_host }}/user/{{ view.request.session.user.uid }}">
				{{ view.request.session.user.name | e }}
			</a>
			<!-- Abmelden -->
		</div>
		<textarea class="comment-form__textarea" name="comment" placeholder="Ihr Kommentar" maxlength="1500"></textarea>
		<input type="hidden" name="nid" value="{{ view.comments.nid }}">
		<input type="hidden" name="pid" value="">
		<input type="hidden" name="uid" value="{{ view.request.session.user.uid }}">
		<input class="comment-form__submit" type="submit" value="Kommentar senden" />
	</form>
{% else -%}
	<div class="comment-login" id="comment-form">
		<div class="comment-login__cta">
			Bitte melden Sie sich an, um zu kommentieren.
		</div>
		<a class="comment-login__button" href="{{ request.registry.settings.community_host }}/user/login?destination={{ request.url|e }}">
			Anmelden
		</a>
		<a class="comment-login__button" href="{{ request.registry.settings.community_host }}/user/register?destination={{ request.url|e }}">
			Registrieren
		</a>
	</div>
{% endif -%}
</section>
