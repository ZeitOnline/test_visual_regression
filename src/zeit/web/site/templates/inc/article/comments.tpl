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
		<a href="#comment-form" class="comment-section__button button">
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
	<div id="js-comments-body" data-action="{{ view.comments.comment_report_url }}" data-auth="{% if request.authenticated_userid %}true{% else %}false{% endif %}">
	{% for comment in view.comments.comments[:20] %}
		<article class="comment{% if comment.is_reply %} comment--indented{% endif %}{% if comment.is_author %} comment--author{% endif %}" id="cid-{{ comment.cid }}">
			<div class="comment__container">
				{% if comment.img_url %}
				<img class="comment__avatar" alt="Avatarbild von {{ comment.name | e }}" src="{{ comment.img_url }}">
				{% endif %}
				<div class="comment__meta">
					{% if comment.is_promoted %}
					<span class="comment__badge comment__badge--promoted" title="Redaktionsempfehlung">&#9733;</span>
					{% endif %}
					{% if comment.is_author %}
					<span class="comment__badge icon-comment-zon-author-badge" title="{{ comment.role }}"></span>
					{% endif %}
					<a class="comment__name" href="{{ comment.userprofile_url }}">
						{{ comment.name | e }}
					</a>
					<span class="comment__recommendations" title="Leserempfehlungen">
					{%- if comment.recommendations -%}
						{{ comment.recommendations }} &#9733;
					{%- endif -%}
					</span>
					<a  class="comment__date" href="#cid-{{ comment.cid }}">
					#{{ loop.index }} &nbsp;/&nbsp; {{ comment.timestamp | format_date_ago() }}
					</a>
				</div>
				<div class="comment__body">
					{{ comment.text | safe }}
				</div>
				<div class="comment__reactions">
					<a class="comment__reaction js-reply-to-comment" data-cid="{{ comment.cid }}" href="#cid-{{ comment.cid }}" title="Antworten">
						<span class="comment__icon icon-comment-reactions-reply"></span>
						<span class="comment__action">Antworten</span>
					</a>
					<a class="comment__reaction js-report-comment" data-cid="{{ comment.cid }}" href="#cid-{{ comment.cid }}" title="Melden">
						<span class="comment__icon icon-comment-reactions-report"></span>
						<span class="comment__action">Melden</span>
					</a>
					<a class="comment__reaction js-recommend-comment" data-cid="{{ comment.cid }}" href="#cid-{{ comment.cid }}" title="Empfehlen">
						<span class="comment__icon icon-comment-reactions-recommend"></span>
						<span class="comment__action">Empfehlen</span>
					</a>
				</div>
			</div>
		</article>
	{% endfor %}
	</div>
{% endif %}

	<div class="comment-section__form">
	{% if request.authenticated_userid -%}
		<form class="comment-form" action="{{ view.comments.comment_post_url }}" method="POST" id="comment-form">
			<div class="comment-form__text">
				{% if request.session.user.picture %}
				<img class="comment-form__avatar" alt="Avatarbild von {{ request.session.user.name | e }}" src="{{ request.session.user.picture }}">
				{% endif %}
				Angemeldet als
				<a class="comment-form__username" href="{{ request.registry.settings.community_host }}/user/{{ request.session.user.uid }}">
					{{ request.session.user.name | e }}
				</a>
				<a class="comment-form__cancel" href="{{ request.registry.settings.community_host }}/logout?destination={{ request.url | e }}">
					Abmelden
				</a>
			</div>
			<textarea class="comment-form__textarea js-required" name="comment" placeholder="Ihr Kommentar" maxlength="1500"></textarea>
			<p class="comment-form__actions">
				<input type="hidden" name="nid" value="{{ view.comments.nid }}">
				<input type="hidden" name="pid" value="">
				<input type="hidden" name="uid" value="{{ request.session.user.uid }}">
				<input class="button" type="submit" value="Kommentar senden" />
			</p>
		</form>
	{% else -%}
		<form class="comment-login" id="comment-form">
			<p>
				Bitte melden Sie sich an, um zu kommentieren.
			</p>
			<a class="button" href="{{ request.registry.settings.community_host }}/user/login?destination={{ request.url | e }}">
				Anmelden
			</a>
			<a class="button" href="{{ request.registry.settings.community_host }}/user/register?destination={{ request.url | e }}">
				Registrieren
			</a>
		</form>
	{% endif -%}
	</div>

	<script type="text/template" id="js-report-comment-template">
		{% if request.authenticated_userid -%}
		<form action="{{ view.comments.comment_report_url }}" method="POST" class="comment-form" style="display: none">
			<textarea name="note" placeholder="Warum halten Sie diesen Kommentar für bedenklich?" class="comment-form__textarea js-required"></textarea>
			<p class="comment-form__text">
				Nutzen Sie dieses Fenster, um Verstöße gegen die <a target="_blank" href="//administratives/2010-03/netiquette">Netiquette</a> zu melden.
				Wenn Sie einem Kommentar inhaltlich widersprechen möchten, <a href="#js-comments-form" class="js-scroll">nutzen Sie das Kommentarformular</a> und beteiligen Sie sich an der Diskussion.
			</p>
			<p class="comment-form__actions">
				<input type="hidden" name="uid" value="{{ request.session.user.uid }}">
				<input type="hidden" name="content_id" value="<% commentId %>">
				<a href="{{ request.url | e }}" class="comment-form__cancel js-cancel-report">Abbrechen</a>
				<button disabled="disabled" class="button js-submit-report" type="button">Abschicken</button>
			</p>
		</form>
		{% else -%}
		<form class="comment-login" style="display: none">
			<p>
				Bitte melden Sie sich an, um diesen Kommentar zu melden.
			</p>
			<a class="button" href="{{ request.registry.settings.community_host }}/user/login?destination={{ request.url | e }}">
				Anmelden
			</a>
			<a class="button" href="{{ request.registry.settings.community_host }}/user/register?destination={{ request.url | e }}">
				Registrieren
			</a>
		</form>
		{% endif -%}
	</script>
</section>
