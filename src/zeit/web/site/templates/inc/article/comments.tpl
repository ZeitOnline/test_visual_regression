<section class="comment-section" id="comments">
	<div class="comment-section__head">
	{% if view.comments and view.comments.comment_count %}
		<span class="comment-section__headline">
			{{ view.comments.comment_count | pluralize('{} Kommentare', '{} Kommentar', '{} Kommentare') }}
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
	<div id="js-comments-body" data-action="{{ view.comments.comment_report_url }}">
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
					#{{ loop.index }} &nbsp;/&nbsp; {{ get_delta_time_from_datetime(comment.timestamp) or (comment.timestamp | format_date) }}
					</a>
				</div>
				<div class="comment__body">
					{{ comment.text | safe }}
				</div>
				<div class="comment__reactions">
					<a class="comment__reaction js-reply-to-comment" data-cid="{{ comment.cid }}" href="{{ view.request | append_get_params(commentpid=comment.cid}) }}#comment-form" title="Antworten">
						<span class="comment__icon icon-comment-reactions-reply"></span>
						<span class="comment__action">Antworten</span>
					</a>
					<a class="comment__reaction js-report-comment" data-cid="{{ comment.cid }}" href="{{ view.request | append_get_params(reportcid=comment.cid) }}#report-comment-form" title="Melden">
						<span class="comment__icon icon-comment-reactions-report"></span>
						<span class="comment__action">Melden</span>
					</a>
					<a class="comment__reaction js-recommend-comment" data-cid="{{ comment.cid }}" data-fans="{{ comment.fans }}" href="#cid-{{ comment.cid }}" title="Empfehlen">
						<span class="comment__icon icon-comment-reactions-recommend"></span>
						<span class="comment__action">Empfehlen</span>
					</a>
				</div>
			</div>
		</article>
	{% endfor %}
	</div>
{% endif %}

	<esi:include src="{{ view.article_url }}/comment-form?commentpid={{ view.request.GET['commentpid'] }}" />

	<script type="text/template" id="js-report-success-template">
		<div class="comment-form__response--success">
			Danke! Ihre Meldung wird an die Redaktion weitergeleitet.
		</div>
	</script>

</section>
